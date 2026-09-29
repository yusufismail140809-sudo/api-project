import sqlite3
from contextlib import contextmanager
from config import DATABASE_URL


@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kode TEXT UNIQUE,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                role TEXT DEFAULT 'user',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cur.execute("PRAGMA table_info(users)")
        cols = {row["name"] for row in cur.fetchall()}
        if "password_hash" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
        if "role" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        if "created_at" not in cols:
            cur.execute("ALTER TABLE users ADD COLUMN created_at TEXT")

        cur.execute("SELECT id FROM users WHERE kode IS NULL OR kode = '' ORDER BY id ASC")
        for row in cur.fetchall():
            uid = row["id"]
            cur.execute("UPDATE users SET kode = ? WHERE id = ?", (f"USR-{uid:03d}", uid))