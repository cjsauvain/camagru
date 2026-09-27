from camagru.lib import png


def blend(photo: bytes, overlay: png.Image) -> png.Image:
    len_photo = len(photo)
    if len_photo != len(overlay.pixels):
        raise ValueError("Photo and overlay must be of the same size.")

    superposition_img = bytearray(len_photo)
    for i in range(0, len_photo, 4):

        a = overlay.pixels[i + 3]

        superposition_img[i] = (overlay.pixels[i] * a + photo[i] * (255 - a)) // 255
        superposition_img[i + 1] = (overlay.pixels[i + 1] * a + photo[i + 1] * (255 - a)) // 255
        superposition_img[i + 2] = (overlay.pixels[i + 2] * a + photo[i + 2] * (255 - a)) // 255
        superposition_img[i + 3] = 255

    return png.Image(overlay.width, overlay.height, bytes(superposition_img))
