from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr, Field

from databasebackend import get_db, init_db
from deps import get_current_user
from schemas import MetaPagination, PageResponse
from services import UserService, UserServiceError

app = FastAPI(title="Belajar Backend", version="3.2")
init_db()


class UserCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    email: Optional[EmailStr] = None


def _handle(err: UserServiceError):
    raise HTTPException(status_code=err.status_code, detail=err.message)


@app.get("/")
def home():
    return {"message": "API jalan"}


@app.get("/users")
def get_users(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = Query("", max_length=50),
):
    with get_db() as conn:
        svc = UserService(conn)
        result = svc.list_users(page, size, search)
    return result


@app.get("/users/{user_id}")
def get_user_by_id(user_id: int):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            user = svc.get_user(user_id)
        except UserServiceError as e:
            _handle(e)
    return user


@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            data = svc.create_user(user.name, user.email)
        except UserServiceError as e:
            _handle(e)
    return {"message": "User dibuat", "data": data}


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            updated = svc.update_user(user_id, user.name, user.email)
        except UserServiceError as e:
            _handle(e)
    return {"updated": updated}


@app.patch("/users/{user_id}")
def patch_user(user_id: int, user: UserUpdate):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            updated = svc.patch_user(user_id, user.name, user.email)
        except UserServiceError as e:
            _handle(e)
    return {"updated": updated}


@app.delete("/users/{user_id}")
def delete_user(user_id: int, current=Depends(get_current_user)):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            deleted = svc.delete_user(user_id, current)
        except UserServiceError as e:
            _handle(e)
    return {"deleted": deleted}