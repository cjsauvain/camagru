import sqlite3

from camagru.db.connection import get_connection
from camagru.models import comment, image
from camagru.services.errors import ValidationError
from camagru.services.validators import validate_comment


def add_comment(user_id: int, image_id: int, body: str) -> int:
    validate_comment(body)

    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            raise ValidationError("Image does not exist.")

        comment_id = comment.create(conn, image_id, user_id, body.strip())
        conn.commit()

    finally:
        conn.close()
    
    return comment_id


def list_comments(image_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        comment_list = comment.find_by_image(conn, image_id)

    finally:
        conn.close()
    
    return comment_list
