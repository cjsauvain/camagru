import sqlite3


def create(
    conn: sqlite3.Connection, session_id: str, user_id: int, lifetime: int
) -> None:
    conn.execute(
        "INSERT INTO sessions (id, user_id, expires_at) "
        "VALUES (?, ?, datetime('now', ?))",
        (session_id, user_id, f"+{lifetime} seconds"),
    )


def find(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM sessions WHERE id = ? AND expires_at > datetime('now')",
        (session_id,),
    ).fetchone()


def delete(conn: sqlite3.Connection, session_id: str) -> None:
    conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))


def delete_for_user(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
