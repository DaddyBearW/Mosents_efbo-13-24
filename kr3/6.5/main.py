import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address


app = FastAPI(title="Task 6.5")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

SECRET_KEY = "another-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db: dict[str, dict[str, str]] = {}


class UserData(BaseModel):
    username: str
    password: str


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "Too many requests"})


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def find_user(username: str) -> tuple[str | None, dict[str, str] | None]:
    for saved_username, user_data in fake_users_db.items():
        if secrets.compare_digest(saved_username, username):
            return saved_username, user_data
    return None, None


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is missing")

    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


@app.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("1/minute")
def register(request: Request, user: UserData) -> dict[str, str]:
    _, existing_user = find_user(user.username)
    if existing_user is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    fake_users_db[user.username] = {
        "hashed_password": get_password_hash(user.password),
    }
    return {"message": "New user created"}


@app.post("/login")
@limiter.limit("5/minute")
def login(request: Request, user: UserData) -> dict[str, str]:
    saved_username, saved_user = find_user(user.username)

    if saved_user is None or saved_username is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(user.password, saved_user["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization failed")

    token = create_access_token({"sub": saved_username})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/protected_resource")
def protected_resource(_: str = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Access granted"}
