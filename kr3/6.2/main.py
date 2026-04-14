import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
from pydantic import BaseModel


app = FastAPI(title="Task 6.2")
security = HTTPBasic()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

fake_users_db: dict[str, dict[str, str]] = {}


class UserBase(BaseModel):
    username: str


class User(UserBase):
    password: str


class UserInDB(UserBase):
    hashed_password: str


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str) -> UserInDB | None:
    for saved_username, user_data in fake_users_db.items():
        if secrets.compare_digest(saved_username, username):
            return UserInDB(username=saved_username, hashed_password=user_data["hashed_password"])
    return None


def auth_user(credentials: HTTPBasicCredentials = Depends(security)) -> UserInDB:
    user = get_user(credentials.username)

    if user is None or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return user


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: User) -> dict[str, str]:
    if get_user(user.username) is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

    fake_users_db[user.username] = {
        "hashed_password": get_password_hash(user.password),
    }
    return {"message": "User added successfully"}


@app.get("/login")
def login(user: UserInDB = Depends(auth_user)) -> dict[str, str]:
    return {"message": f"Welcome, {user.username}!"}
