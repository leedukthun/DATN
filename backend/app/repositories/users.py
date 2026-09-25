from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username.strip().lower()))


def create_user(db: Session, username: str, password_hash: str) -> User:
    user = User(username=username.strip().lower(), password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
