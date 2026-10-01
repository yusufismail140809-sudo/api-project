from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict, Any


class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def _cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)

    # --- READ ---
    def get_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        cur = self._cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        cur = self._cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None

    def list_paginated(
        self,
        page: int = 1,
        size: int = 10,
        search: str = "",
    ) -> tuple[List[Dict[str, Any]], int]:
        offset = (page - 1) * size
        cur = self._cursor()

        if search:
            where = "WHERE name ILIKE %s OR email ILIKE %s"
            params = [f"%{search}%", f"%{search}%"]
        else:
            where = ""
            params = []

        cur.execute(f"SELECT COUNT(*) AS count FROM users {where}", params)
        total = cur.fetchone()["count"]

        cur.execute(
            f"""
            SELECT id, kode, name, email, role, created_at
            FROM users {where}
            ORDER BY id ASC
            LIMIT %s OFFSET %s
            """,
            params + [size, offset],
        )
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows, total

    # --- WRITE ---
    def create(
        self,
        name: str,
        email: str,
        password_hash: Optional[str] = None,
        role: str = "user",
    ) -> int:
        cur = self._cursor()
        cur.execute(
            """
            INSERT INTO users (name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (name, email, password_hash, role),
        )
        user_id = cur.fetchone()["id"]
        cur.execute(
            "UPDATE users SET kode = %s WHERE id = %s",
            (f"USR-{user_id:03d}", user_id),
        )
        cur.close()
        return user_id

    def update(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> bool:
        existing = self.get_by_id(user_id)
        if not existing:
            return False

        new_name = name if name is not None else existing["name"]
        new_email = email if email is not None else existing["email"]

        cur = self._cursor()
        cur.execute(
            "UPDATE users SET name = %s, email = %s WHERE id = %s",
            (new_name, new_email, user_id),
        )
        cur.close()
        return True

    def delete(self, user_id: int) -> bool:
        cur = self._cursor()
        cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
        cur.close()
        return True