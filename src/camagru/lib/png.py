from dataclasses import dataclass
import zlib

PNG_SIG = bytes([137, 80, 78, 71, 13, 10, 26, 10])
IHDR = b"IHDR"
IDAT = b"IDAT"
IEND = b"IEND"


@dataclass
class Image:
    width: int
    height: int
    pixels: bytes
    bit_depth: int = 8
    color_type: int = 6
    compression_method: int = 0
    filter_method: int = 0
    interlace_method: int = 0


def _validate_ihdr_chunk(data: bytes):
    # Check bit depth
    if data[8] != 8:
        raise ValueError("Please use a bit depth of 8")
    # Check color type
    if data[9] != 6:
        raise ValueError("Please use color type 6 (RGBA)")
    # Check compression method
    if data[10] != 0:
        raise ValueError(
            "Unknown compression method, please use method 0 (deflate/inflate)"
        )
    # Check filter method
    if data[11] != 0:
        raise ValueError(
            "Unknown filter method, please use method 0 (adaptive filtering)"
        )
    # Check interlace method
    if data[12] != 0:
        raise ValueError("Please use interlace method 0 (no interlace)")


def _extract_ihdr_chunk(chunk_data: bytes):
    chunk_data_len = int.from_bytes(chunk_data[:4], byteorder="big")
    data = chunk_data[8:8+chunk_data_len]
    _validate_ihdr_chunk(data)

    crc_stored = int.from_bytes(chunk_data[8+chunk_data_len:], byteorder="big")
    crc_computed = zlib.crc32(IHDR + data)

    return {
        "type": IHDR,
        "width": int.from_bytes(data[:4]),
        "height": int.from_bytes(data[4:8]),
        "bit_depth": data[8],
        "color_type": data[9],
        "compression_method": data[10],
        "filter_method": data[11],
        "interlace_method": data[12],
        "crc": crc_stored,
        "crc_computed": crc_computed,
    }


def _extract_idat_chunk(chunk_data: bytes):
    chunk_data_len = int.from_bytes(chunk_data[:4], byteorder="big")

    data = chunk_data[8:8+chunk_data_len]
    crc_stored = int.from_bytes(chunk_data[8+chunk_data_len:], byteorder="big")
    crc_computed = zlib.crc32(IDAT + data)

    return {
        "type": IDAT,
        "length": chunk_data_len,
        "data": data,
        "crc": crc_stored,
        "crc_computed": crc_computed,
    }


def _paeth_predictor(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)

    if pa <= pb and pa <= pc:
        return a
    elif pb <= pc:
        return b
    return c


def _defilter(scanlines: bytes, width: int, height: int) -> bytes:
    stride, bpp = (width * 4), 4
    out = bytearray()
    prev = bytearray(stride)
    pos = 0

    for line_index in range(height):
        ftype = scanlines[pos]
        if ftype > 4:
            raise ValueError(f"Unknown filter method: {ftype}")

        line = bytearray(scanlines[pos+1:pos+stride+1])
        pos += stride + 1

        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0

            if ftype == 1:
                line[i] = (line[i] + a) & 0xFF
            elif ftype == 2:
                line[i] = (line[i] + b) & 0xFF
            elif ftype == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif ftype == 4:
                line[i] = (line[i] + _paeth_predictor(a, b, c)) & 0xFF

        out += line
        prev = line

    return bytes(out)


def _retrieve_chunk(chunk_data: bytes) -> dict:
    chunk_type = chunk_data[4:8]
    if chunk_type == IEND:
        return {"type": IEND}
    elif chunk_type == IHDR:
        chunk = _extract_ihdr_chunk(chunk_data)
    elif chunk_type == IDAT:
        chunk = _extract_idat_chunk(chunk_data)
    else:
        return {"type": chunk_type}

    if chunk["crc"] != chunk["crc_computed"]:
        raise ValueError(
            f"PNG file is corrupted: Invalid CRC for chunk {chunk_type}"
        )

    return chunk


def decode(data: bytes) -> Image:
    if data[:8] != PNG_SIG:
        raise TypeError("PNG is the only supported format.")

    width = height = None
    idat_data_compressed = bytearray()
    begin_offset = 8

    while begin_offset < len(data):
        chunk_data_len = int.from_bytes(data[begin_offset:begin_offset+4])
        end_offset = begin_offset + 4 + 4 + chunk_data_len + 4

        chunk = _retrieve_chunk(data[begin_offset:end_offset])
        if chunk["type"] == IHDR:
            width = int(chunk["width"])
            height = int(chunk["height"])
        elif chunk["type"] == IDAT:
            idat_data_compressed.extend(chunk["data"])
        elif chunk["type"] == IEND:
            break
        begin_offset = end_offset

    if width is None or height is None:
        raise ValueError("Missing IHDR chunk.")

    scanlines = zlib.decompress(idat_data_compressed)
    if len(scanlines) != height * (1 + width * 4):
        raise ValueError("Image data invalid.")

    pixels = _defilter(scanlines, width, height)

    return Image(width=width, height=height, pixels=pixels)


def _build_chunk(type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(type + data)

    return (
        len(data).to_bytes(4, byteorder="big")
        + type
        + data
        + crc.to_bytes(4, byteorder="big")
    )


def _build_ihdr_chunk(image: Image) -> bytes:
    ihdr_chunk_data = bytes(
        image.width.to_bytes(4, byteorder="big")
        + image.height.to_bytes(4, byteorder="big")
        + image.bit_depth.to_bytes(1, byteorder="big")
        + image.color_type.to_bytes(1, byteorder="big")
        + image.compression_method.to_bytes(1, byteorder="big")
        + image.filter_method.to_bytes(1, byteorder="big")
        + image.interlace_method.to_bytes(1, byteorder="big")
    )
    return _build_chunk(IHDR, ihdr_chunk_data)


def _build_iend_chunk() -> bytes:
    return _build_chunk(IEND, b"")


def _build_idat_chunk(pixels: bytes) -> bytes:
    return _build_chunk(IDAT, zlib.compress(pixels))


def encode(image: Image) -> bytes:
    stride = image.width * 4
    scanlines = b"".join(
        b"\x00" + image.pixels[y*stride:(y+1)*stride]
        for y in range(image.height)
    )
    ihdr_chunk = _build_ihdr_chunk(image)
    idat_chunk = _build_idat_chunk(scanlines)
    iend_chunk = _build_iend_chunk()

    return PNG_SIG + ihdr_chunk + idat_chunk + iend_chunk
