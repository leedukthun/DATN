from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import users as repository
from app.schemas.auth import LoginRequest, RegisterRequest, UserRead

router = APIRouter(prefix="/auth", tags=["Auth"])


def _auth_response(user: User) -> dict:
    return {
        "access_token": create_access_token(user_id=user.id, username=user.username),
        "token_type": "bearer",
        "user": UserRead.model_validate(user).model_dump(),
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip().lower()
    if repository.get_user_by_username(db, username):
        raise HTTPException(status_code=409, detail="Tên đăng nhập đã tồn tại.")
    user = repository.create_user(db, username, hash_password(payload.password))
    return _auth_response(user)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = repository.get_user_by_username(db, payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Tên đăng nhập hoặc mật khẩu không đúng.")
    return _auth_response(user)


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)
