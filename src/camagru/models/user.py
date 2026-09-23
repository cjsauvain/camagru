import sqlite3


def create(
    conn: sqlite3.Connection,
    username: str,
    email: str,
    password_hash: str,
    confirm_token: str,
) -> int:
    cursor = conn.execute(
        "INSERT INTO users (username, email, password, confirm_token) VALUES (?, ?, ?, ?)",
        (username, email, password_hash, confirm_token),
    )

    if cursor.lastrowid is None:
        raise RuntimeError("INSERT produced no row id.")

    return cursor.lastrowid


def find_by_username(conn: sqlite3.Connection, username: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()


def find_by_email(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def find_by_confirm_token(
    conn: sqlite3.Connection, confirm_token: str
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE confirm_token = ?", (confirm_token,)
    ).fetchone()


def find_by_reset_token(
    conn: sqlite3.Connection, reset_token: str
) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE reset_token = ? AND reset_expires_at > datetime('now')",
        (reset_token,)
    ).fetchone()


def find_by_id(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def confirm(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute(
        "UPDATE users SET is_confirmed = 1, confirm_token = NULL WHERE id = ?",
        (user_id,),
    )


def set_reset_token(conn: sqlite3.Connection, user_id: int, reset_token: str, lifetime: int) -> None:
    conn.execute(
        "UPDATE users SET reset_token = ?, reset_expires_at = datetime('now', ?) WHERE id = ?",
        (reset_token, f"+{lifetime} seconds", user_id)
    )


def set_password(conn: sqlite3.Connection, user_id: int, password_hash: str) -> None:
    conn.execute(
        "UPDATE users SET password = ?, reset_token = NULL, reset_expires_at = NULL WHERE id = ?",
        (password_hash, user_id)
    )