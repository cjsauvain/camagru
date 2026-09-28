import sqlite3


def create(conn: sqlite3.Connection, image_id: int, user_id: int) -> None:
    conn.execute(
        "INSERT INTO likes (image_id, user_id) VALUES (?, ?)",
        (image_id, user_id)
    )


def delete(conn: sqlite3.Connection, image_id: int, user_id: int) -> None:
    conn.execute(
        "DELETE FROM likes WHERE image_id = ? AND user_id = ?",
        (image_id, user_id)
    )


def exists(conn: sqlite3.Connection, image_id: int, user_id: int) -> bool:
    return conn.execute(
        "SELECT 1 FROM likes WHERE image_id = ? AND user_id = ?",
        (image_id, user_id)
    ).fetchone() is not None
