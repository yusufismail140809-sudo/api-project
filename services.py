from typing import Optional
from databasebackend import get_db
from repositories import UserRepository
from security import hash_password, verify_password, create_access_token


class UserServiceError(Exception):
    """Error dari business logic, akan diterjemahkan jadi HTTP di router."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class UserService:
    def __init__(self, conn):
        self.conn = conn
        self.repo = UserRepository(conn)

    # --- REGISTER ---
    def register(self, name: str, email: str, password: str) -> dict:
        if self.repo.get_by_email(email):
            raise UserServiceError("Email sudah terdaftar", 400)

        user_id = self.repo.create(
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        return {"id": user_id, "kode": f"USR-{user_id:03d}"}

    # --- LOGIN ---
    def login(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not user["password_hash"]:
            raise UserServiceError("Kredensial tidak valid", 401)
        if not verify_password(password, user["password_hash"]):
            raise UserServiceError("Kredensial tidak valid", 401)
        return create_access_token({"sub": str(user["id"]), "role": user["role"]})

    # --- LIST (pagination) ---
    def list_users(self, page: int, size: int, search: str) -> dict:
        rows, total = self.repo.list_paginated(page, size, search)
        import math
        total_pages = math.ceil(total / size) if total > 0 else 1
        return {
            "meta": {
                "page": page,
                "size": size,
                "total_records": total,
                "total_pages": total_pages,
            },
            "data": rows,
        }

    # --- GET ONE ---
    def get_user(self, user_id: int) -> dict:
        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserServiceError("User gak ketemu", 404)
        return user

    # --- CREATE (admin-style, tanpa password) ---
    def create_user(self, name: str, email: str) -> dict:
        if self.repo.get_by_email(email):
            raise UserServiceError("Email udah dipake", 400)
        user_id = self.repo.create(name=name, email=email)
        return {"id": user_id, "kode": f"USR-{user_id:03d}", "name": name, "email": email}

    # --- UPDATE (full) ---
    def update_user(self, user_id: int, name: str, email: str) -> dict:
        existing = self.repo.get_by_id(user_id)
        if not existing:
            raise UserServiceError("User gak ketemu", 404)

        # email dipakai orang lain?
        other = self.repo.get_by_email(email)
        if other and other["id"] != user_id:
            raise UserServiceError("Email dipake orang lain", 400)

        self.repo.update(user_id, name=name, email=email)
        return self.repo.get_by_id(user_id)

    # --- PATCH (partial) ---
    def patch_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
    ) -> dict:
        if email:
            other = self.repo.get_by_email(email)
            if other and other["id"] != user_id:
                raise UserServiceError("Email dipake orang lain", 400)
        if not self.repo.update(user_id, name=name, email=email):
            raise UserServiceError("User gak ketemu", 404)
        return self.repo.get_by_id(user_id)

    # --- DELETE ---
    def delete_user(self, user_id: int, requester: dict) -> dict:
        if requester["id"] != user_id and requester.get("role") != "admin":
            raise UserServiceError("Gak boleh hapus user lain", 403)

        user = self.repo.get_by_id(user_id)
        if not user:
            raise UserServiceError("User gak ketemu", 404)

        self.repo.delete(user_id)
        return user