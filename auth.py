from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from databasebackend import get_db
from schemas import UserRegister, TokenResponse
from services import UserService, UserServiceError
from deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def _handle(err: UserServiceError):
    raise HTTPException(status_code=err.status_code, detail=err.message)


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            result = svc.register(payload.name, payload.email, payload.password)
        except UserServiceError as e:
            _handle(e)
    return {"message": "Registrasi berhasil", "kode": result["kode"]}


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_db() as conn:
        svc = UserService(conn)
        try:
            token = svc.login(form_data.username, form_data.password)
        except UserServiceError as e:
            _handle(e)
    return TokenResponse(access_token=token)


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "kode": current_user["kode"],
        "name": current_user["name"],
        "email": current_user["email"],
        "role": current_user["role"],
    }