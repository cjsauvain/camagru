from camagru.db.connection import get_connection
from pathlib import Path


def init():
    sql = (Path(__file__).parent / "schema.sql").read_text()

    conn = get_connection()
    try:
        # Enable WAL mode: allows concurrent reads while a write is in progress
        conn.execute("PRAGMA journal_mode = WAL")

        conn.executescript(sql)
        conn.commit()

    finally:
        conn.close()


if __name__ == "__main__":
    init()
