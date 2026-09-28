import sqlite3

from camagru.services.errors import ValidationError

PER_PAGE = 5


def create(conn: sqlite3.Connection, user_id: int, filename: str) -> int:
    cursor = conn.execute(
        "INSERT INTO images (user_id, filename) VALUES (?, ?)", (user_id, filename)
    )

    if cursor.lastrowid is None:
        raise RuntimeError("INSERT produced no row id.")

    return cursor.lastrowid


def find_by_id(conn: sqlite3.Connection, image_id: int) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM images WHERE id = ?", (image_id,)).fetchone()


def find_by_user(conn: sqlite3.Connection, user_id: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT * FROM images WHERE user_id = ? ORDER BY created_at DESC, id DESC",
        (user_id,),
    ).fetchall()


def count(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM images").fetchone()[0]


def find_page(conn: sqlite3.Connection, limit: int, offset: int) -> list[sqlite3.Row]:
    return conn.execute(
        "SELECT images.id, images.user_id, images.created_at, users.username "
        "FROM images "
        "JOIN users ON users.id = images.user_id "
        "ORDER BY images.created_at DESC, images.id DESC "
        "LIMIT ? OFFSET ?",
        (limit, offset),
    ).fetchall()


def delete(conn: sqlite3.Connection, image_id: int) -> None:
    conn.execute(
        "DELETE FROM images WHERE id = ?", (image_id,)
    )