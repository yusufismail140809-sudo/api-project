from pydantic import BaseModel, EmailStr, Field
from typing import Generic, TypeVar, List

T = TypeVar("T")

class UserRegister(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MetaPagination(BaseModel):
    page: int
    size: int
    total_records: int
    total_pages: int

class PageResponse(BaseModel, Generic[T]):
    meta: MetaPagination
    data: List[T]