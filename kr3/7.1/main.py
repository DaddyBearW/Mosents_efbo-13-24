from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel


app = FastAPI(title="Task 7.1")
security = HTTPBearer()

SECRET_KEY = "rbac-secret-key"
ALGORITHM = "HS256"

fake_users_db = {
    "admin1": {"password": "admin123", "role": "admin"},
    "user1": {"password": "user123", "role": "user"},
    "guest1": {"password": "guest123", "role": "guest"},
}


class LoginData(BaseModel):
    username: str
    password: str


def create_access_token(username: str, role: str) -> str:
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict[str, str]:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        role = payload.get("role")
        if not username or not role:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


def require_roles(*allowed_roles: str):
    def checker(user: dict[str, str] = Depends(get_current_user)) -> dict[str, str]:
        if user["role"] not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user

    return checker


@app.post("/login")
def login(data: LoginData) -> dict[str, str]:
    user = fake_users_db.get(data.username)
    if user is None or user["password"] != data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(data.username, user["role"])
    return {"access_token": token, "token_type": "bearer", "role": user["role"]}


@app.get("/protected_resource")
def protected_resource(user: dict[str, str] = Depends(require_roles("admin", "user"))) -> dict[str, str]:
    return {"message": f"Access granted for {user['role']}"}


@app.post("/admin/resource")
def admin_resource(user: dict[str, str] = Depends(require_roles("admin"))) -> dict[str, str]:
    return {"message": f"Resource created by {user['username']}"}


@app.put("/user/resource")
def user_resource(user: dict[str, str] = Depends(require_roles("admin", "user"))) -> dict[str, str]:
    return {"message": f"Resource updated by {user['username']}"}


@app.get("/guest/resource")
def guest_resource(user: dict[str, str] = Depends(require_roles("admin", "user", "guest"))) -> dict[str, str]:
    return {"message": f"Resource read by {user['username']}"}
