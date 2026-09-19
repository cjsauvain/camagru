import os
import sqlite3


def get_connection() -> sqlite3.Connection:
    db_path = os.environ.get("DB_PATH", "data/camagru.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)

    # Change how each lines are read
    conn.row_factory = sqlite3.Row
    # Turn on foreign keys
    conn.execute("PRAGMA foreign_keys = ON")
    # For concurrency
    conn.execute("PRAGMA busy_timeout = 5000")

    return conn
