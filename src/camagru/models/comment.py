import sqlite3


def create(conn: sqlite3.Connection, image_id: int, user_id: int, body: str) -> int:
    cursor = conn.execute(
        "INSERT INTO comments (image_id, user_id, body) VALUES (?, ?, ?)",
        (image_id, user_id, body)
    )

    if cursor.lastrowid is None:
        raise RuntimeError("INSERT produced no row id.")

    return cursor.lastrowid


def find_by_image(conn: sqlite3.Connection, image_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT comments.body, comments.created_at, users.username "
        "FROM comments " 
        "JOIN users ON users.id = comments.user_id "
        "WHERE comments.image_id = ? "
        "ORDER BY comments.created_at ASC, comments.id ASC",
        (image_id,)
    ).fetchall()