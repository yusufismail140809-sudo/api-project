import sqlite3
from typing import Optional, List, Dict, Any


class UserRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # --- READ ---
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cur.fetchone()
        return dict(row) if row else None

    def list_paginated(
        self,
        page: int = 1,
        size: int = 10,
        search: str = "",
    ) -> tuple[List[Dict[str, Any]], int]:
        """Return (list_user, total_records)."""
        offset = (page - 1) * size
        cur = self.conn.cursor()

        if search:
            where = "WHERE name LIKE ? OR email LIKE ?"
            params = [f"%{search}%", f"%{search}%"]
        else:
            where = ""
            params = []

        cur.execute(f"SELECT COUNT(*) FROM users {where}", params)
        total = cur.fetchone()[0]

        cur.execute(
            f"""
            SELECT id, kode, name, email, role, created_at
            FROM users {where}
            ORDER BY id ASC
            LIMIT ? OFFSET ?
            """,
            params + [size, offset],
        )
        rows = [dict(r) for r in cur.fetchall()]
        return rows, total

    # --- WRITE ---
    def create(
        self,
        name: str,
        email: str,
        password_hash: Optional[str] = None,
        role: str = "user",
    ) -> int:
        cur = self.conn.cursor()
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, password_hash, role),
        )
        user_id = cur.lastrowid
        # langsung isi kode pakai id yang baru
        cur.execute(
            "UPDATE users SET kode = ? WHERE id = ?",
            (f"USR-{user_id:03d}", user_id),
        )
        return user_id

    def update(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        # ambil dulu data lama (partial update)
        existing = self.get_by_id(user_id)
        if not existing:
            return False

        new_name = name if name is not None else existing["name"]
        new_email = email if email is not None else existing["email"]

        cur = self.conn.cursor()
        cur.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (new_name, new_email, user_id),
        )
        return cur.rowcount > 0

    def delete(self, user_id: int) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cur.rowcount > 0