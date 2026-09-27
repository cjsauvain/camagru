import sqlite3


def create(conn: sqlite3.Connection, user_id: int, filename: str) -> int:
    cursor = conn.execute(
        "INSERT INTO images (user_id, filename) VALUES (?, ?)",
        (user_id, filename)
    )
    
    if cursor.lastrowid is None:
        raise RuntimeError("INSERT produced no row id.")

    return cursor.lastrowid


def find_by_id(conn: sqlite3.Connection, image_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM images WHERE id = ?", (image_id,)
    ).fetchone()


def find_by_user(conn: sqlite3.Connection, user_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM images WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    ).fetchall()
