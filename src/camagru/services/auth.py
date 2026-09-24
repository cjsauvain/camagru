import os
import sqlite3

from camagru.db.connection import get_connection
from camagru.lib.mail import send_mail
from camagru.lib.security import generate_token, hash_password, verify_password
from camagru.services.errors import ValidationError
from camagru.models import session
from camagru.models.user import (
    confirm,
    create,
    find_by_confirm_token,
    find_by_email,
    find_by_id,
    find_by_reset_token,
    find_by_username,
    set_password,
    set_reset_token
)
from camagru.services.validators import (
    validate_email,
    validate_password,
    validate_username
)


SESSION_LIFETIME = 86400
RESET_TOKEN_LIFETIME = 3600


def _validate_params(username: str, email: str, password: str) -> None:
    validate_username(username)
    validate_email(email)
    validate_password(password)


def register(username: str, email: str, password: str) -> int:
    _validate_params(username, email, password)

    confirm_token = generate_token()
    conn = get_connection()
    try:
        if find_by_username(conn, username):
            raise ValidationError("This username is not available.")
        if find_by_email(conn, email):
            raise ValidationError("This email is already registered.")

        user_id = create(conn, username, email, hash_password(password), confirm_token)
        conn.commit()

    except sqlite3.IntegrityError as e:
        raise ValidationError("This username or email is already registered.") from e

    finally:
        conn.close()

    app_url = os.environ.get("APP_URL", "http://localhost:8080")
    confirm_url = f"{app_url}/register/confirm/{confirm_token}"
    send_mail(
        email,
        "Last step before account activation",
        f"Confirm your Camagru account: {confirm_url}",
    )

    return user_id


def confirm_account(confirm_token: str) -> None:
    conn = get_connection()

    try:
        user = find_by_confirm_token(conn, confirm_token)
        if user is None:
            raise ValidationError("Confirmation token is invalid.")

        confirm(conn, user["id"])
        conn.commit()

    finally:
        conn.close()


def login(username: str, password: str) -> str:
    conn = get_connection()

    try:
        user = find_by_username(conn, username)
        if user is None or not verify_password(password, user["password"]):
            raise ValidationError("Invalid username or password.")
        if not user["is_confirmed"]:
            raise ValidationError(
                "Please confirm your account first. Check your emails."
            )
        
        session_id = generate_token()
        session.create(conn, session_id, user["id"], SESSION_LIFETIME)
        conn.commit()

    finally:
        conn.close()

    return session_id


def current_user(session_id: str | None) -> sqlite3.Row | None:
    if not session_id:
        return None
    
    conn = get_connection()
    try:
        row = session.find(conn, session_id)
        if row is None:
            return None
        
        return find_by_id(conn, row["user_id"])
    
    finally:
        conn.close()


def logout_user(session_id: str | None) -> None:
    if not session_id:
        return
    
    conn = get_connection()
    try:
        session.delete(conn, session_id)
        conn.commit()

    finally:
        conn.close()


def request_password_reset(email: str) -> None:
    conn = get_connection()
    try:
        user = find_by_email(conn, email)
        if user is None:
            return
        reset_token = generate_token()
        set_reset_token(conn, user["id"], reset_token, RESET_TOKEN_LIFETIME)
        conn.commit()
    finally:
        conn.close()

    app_url = os.environ.get("APP_URL", "http://localhost:8080")
    reset_url = f"{app_url}/reset-password/{reset_token}"
    send_mail(email, "Password Reset", f"Reset your password: {reset_url}")


def reset_password(reset_token: str, new_password: str) -> None:
    validate_password(new_password)
    conn = get_connection()
    try:
        user = find_by_reset_token(conn, reset_token)
        if user is None:
            raise ValidationError("This reset link is invalid or has expired.")
        set_password(conn, user["id"], hash_password(password=new_password))
        session.delete_for_user(conn, user["id"])
        conn.commit()

    finally:
        conn.close()
