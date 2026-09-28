import os
import sqlite3

from camagru.db.connection import get_connection
from camagru.lib.mail import send_mail
from camagru.models import comment, image, user
from camagru.services.errors import ValidationError
from camagru.services.validators import validate_comment


def add_comment(user_id: int, image_id: int, body: str) -> int:
    validate_comment(body)

    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            raise ValidationError("Image does not exist.")
        
        author = user.find_by_id(conn, img["user_id"])
        commentator = user.find_by_id(conn, user_id)

        comment_id = comment.create(conn, image_id, user_id, body.strip())
        conn.commit()

    finally:
        conn.close()
    
    if author and commentator and author["notify_on_comment"] \
        and author["id"] != user_id:
        try:
            send_mail(
                author["email"],
                f"{commentator['username']} commented on your photo",
                f"{body.strip()}\n\n{os.environ.get('APP_URL', 'http://localhost:8080') + '/gallery'}"
            )
        except OSError:
            pass

    return comment_id


def list_comments(image_id: int) -> list[sqlite3.Row]:
    conn = get_connection()
    try:
        comment_list = comment.find_by_image(conn, image_id)

    finally:
        conn.close()
    
    return comment_list
