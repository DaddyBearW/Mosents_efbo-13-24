from fastapi import Depends, Header, HTTPException

from app.schemas import User
from app.storage import task_storage


def get_current_user(
    x_user_id: str | None = Header(default=None),
    x_user_role: str = Header(default="user"),
) -> User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header is required")

    try:
        user_id = int(x_user_id)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id header") from exc

    role = x_user_role.strip().lower()
    if role not in {"user", "admin"}:
        role = "user"

    return User(id=user_id, role=role)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_storage():
    return task_storage
