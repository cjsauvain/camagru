import os
from pathlib import Path
import secrets

from camagru.db.connection import get_connection
from camagru.lib import overlays, png
from camagru.lib.compose import blend
from camagru.models import image
from camagru.services.errors import ValidationError

PHOTO_SIZE = 1_228_800
IMAGE_DIR = Path(
    os.environ.get(
        "DB_PATH", "data/camagru.db"
    )
).parent / "images"


def create_image(user_id: int, photo: bytes, overlay_name: str) -> int:
    if len(photo) != PHOTO_SIZE:
        raise ValidationError("Photo must be 640x480.")

    overlay = overlays.get(overlay_name)
    if overlay is None:
        raise ValidationError("Overlay does not exist.")

    superposition_img = blend(photo, overlay)
    encoded_img = png.encode(superposition_img)
    filename = secrets.token_hex(16) + ".png"
    os.makedirs(IMAGE_DIR, exist_ok=True)

    filepath = IMAGE_DIR / filename
    filepath.write_bytes(encoded_img)

    conn = get_connection()
    try:
        image_id = image.create(conn, user_id, filename)
        conn.commit()

    except Exception:
        filepath.unlink(missing_ok=True)
        raise

    finally:
        conn.close()

    return image_id


def image_path(image_id: int) -> Path | None:
    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            return None

    finally:
        conn.close()

    return IMAGE_DIR / img["filename"]