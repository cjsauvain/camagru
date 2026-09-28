from camagru.db.connection import get_connection
from camagru.models import image, like
from camagru.services.errors import ValidationError


def toggle_like(user_id: int, image_id: int) -> None:
    conn = get_connection()
    try:
        img = image.find_by_id(conn, image_id)
        if img is None:
            raise ValidationError("Image does not exist.")
        
        if like.exists(conn, image_id, user_id):
            like.delete(conn, image_id, user_id)
        else:
            like.create(conn, image_id, user_id)
        
        conn.commit()

    finally:
        conn.close()
