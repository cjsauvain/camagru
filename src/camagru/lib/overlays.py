from pathlib import Path
from camagru.lib import png

OVERLAYS_DIR = Path(__file__).parent.parent / "static" / "overlays"
OVERLAY_FILES: dict[str, str] = {
    "cat": "cat.png",
    "hat": "hat.png",
    "frame": "frame.png",
}
OVERLAYS: dict[str, png.Image] = {}


def load() -> None:
    for name, filename in OVERLAY_FILES.items():
        filepath = OVERLAYS_DIR / filename
        img = png.decode(filepath.read_bytes())
        if (img.width, img.height) != (640, 480):
            raise ValueError(
                f"{filename}: expected 640x480, got {img.width}x{img.height}"
            )
        if min(img.pixels[3::4]) != 0:
            raise ValueError(f"{filename}: no transparent pixel, it would hide the whole photo.")
        OVERLAYS[name] = img


def get(overlay_id: str) -> png.Image | None:
    return OVERLAYS.get(overlay_id)
