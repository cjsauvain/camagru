import math
import os
from pathlib import Path
import secrets
import sqlite3

from camagru.db.connection import get_connection
from camagru.lib import overlays, png
from camagru.lib.compose import blend
from camagru.models import image
from camagru.models.image import PER_PAGE
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


def delete_image(user_id: int, image_id: int) -> None:
    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            raise ValidationError("Image does not exist.")
        elif img["user_id"] != user_id:
            raise ValidationError("This image is not yours.")
        image.delete(conn, image_id)
        conn.commit()
        image_filename = IMAGE_DIR / img["filename"]
        image_filename.unlink(missing_ok=True)

    finally:
        conn.close()


def image_path(image_id: int) -> Path | None:
    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            return None

    finally:
        conn.close()

    return IMAGE_DIR / img["filename"]


def list_user_images(user_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        images = image.find_by_user(conn, user_id)

    finally:
        conn.close()

    return images


def list_gallery(page_index: int) -> tuple[list[sqlite3.Row], int]:
    if page_index < 1:
        raise ValidationError("Page not found.")

    conn = get_connection()
    try:
        page_count = math.ceil(image.count(conn) / PER_PAGE)
        if page_index > max(page_count, 1):
            raise ValidationError("Page does not exist.")

        page_images = image.find_page(conn, PER_PAGE, (page_index - 1) * PER_PAGE)

    finally:
        conn.close()
    
    return page_images, page_count
