from camagru.db.connection import get_connection
from camagru.lib import overlays, png
from camagru.lib.compose import blend
from camagru.services.errors import ValidationError

PHOTO_SIZE = 1_228_800


def create_image(user_id: int, photo: bytes, overlay_name: str) -> int:
    if len(photo) != PHOTO_SIZE:
        raise ValidationError("Photo is too large.")

    overlay = overlays.get(overlay_name)
    if overlay is None:
        raise ValidationError("Overlay does not exist.")

    conn = get_connection()
    try:
        superposition_img = blend(photo, overlay)
        encoded_img = png.encode(superposition_img)

    finally:
        conn.close()
