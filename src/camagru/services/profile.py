from camagru.lib.security import hash_password, verify_password
from camagru.models.user import (
    find_by_email,
    find_by_id,
    find_by_username,
    set_email,
    set_notification,
    set_password,
    set_username
)
from camagru.db.connection import get_connection
from camagru.services.errors import ValidationError
from camagru.services.validators import validate_email, validate_password, validate_username


def update_username(user_id: int, username: str) -> None:
    validate_username(username)

    conn = get_connection()
    try:
        existing_username = find_by_username(conn, username)
        if existing_username is not None and existing_username["id"] != user_id:
            raise ValidationError("This username is not available.")

        set_username(conn, user_id, username)
        conn.commit()

    finally:
        conn.close()


def update_email(user_id: int, email: str) -> None:
    validate_email(email)

    conn = get_connection()
    try:
        existing_email = find_by_email(conn, email)
        if existing_email is not None and existing_email["id"] != user_id:
            raise ValidationError("This email is already registered.")

        set_email(conn, user_id, email)
        conn.commit()

    finally:
        conn.close()


def change_password(user_id: int, current_password: str, new_password: str) -> None:
    validate_password(new_password)

    conn = get_connection()
    try:
        user = find_by_id(conn, user_id)
        if user is None:
            raise ValidationError("This user does not exist.")
            
        if verify_password(current_password, user["password"]) is False:
            raise ValidationError("Incorrect Password.")
        
        set_password(conn, user_id, hash_password(new_password))
        conn.commit()

    finally:
        conn.close()


def update_notification(user_id: int, enabled: bool) -> None:
    conn = get_connection()
    try:
        set_notification(conn, user_id, enabled)
        conn.commit()

    finally:
        conn.close()
