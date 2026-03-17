import time
import uuid

from fastapi import Cookie, FastAPI, HTTPException, Request, Response, status
from itsdangerous import BadSignature, Signer
from pydantic import BaseModel, ValidationError


app = FastAPI(title="Task 5.3")

SECRET_KEY = "super-secret-key-for-task-5-3"
SESSION_LIFETIME_SECONDS = 300
SESSION_REFRESH_THRESHOLD_SECONDS = 180

signer = Signer(SECRET_KEY)

VALID_USERS = {
    "user123": {
        "password": "password123",
        "full_name": "Test User",
        "email": "user123@example.com",
    }
}
user_profiles: dict[str, dict[str, str]] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


def build_signed_token(user_id: str, last_activity: int) -> str:
    payload = f"{user_id}.{last_activity}"
    return signer.sign(payload).decode()


def unauthorized_response(message: str, response: Response | None = None) -> dict[str, str]:
    if response is not None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"message": message}


def parse_signed_token(token: str) -> tuple[str, int]:
    try:
        payload = signer.unsign(token).decode()
    except BadSignature:
        raise ValueError("Invalid session")

    parts = payload.split(".")
    if len(parts) != 2:
        raise ValueError("Invalid session")

    user_id, timestamp_raw = parts
    try:
        uuid.UUID(user_id)
        last_activity = int(timestamp_raw)
    except (ValueError, TypeError):
        raise ValueError("Invalid session")

    return user_id, last_activity


async def parse_login_request(request: Request) -> LoginRequest:
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        payload = await request.json()
    else:
        form_data = await request.form()
        payload = dict(form_data)
    try:
        return LoginRequest.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc


@app.post("/login")
async def login(request: Request, response: Response) -> dict[str, str]:
    data = await parse_login_request(request)
    user = VALID_USERS.get(data.username)
    if user is None or user["password"] != data.password:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"message": "Invalid credentials"}

    user_id = str(uuid.uuid4())
    user_profiles[user_id] = {
        "username": data.username,
        "full_name": user["full_name"],
        "email": user["email"],
    }
    current_time = int(time.time())
    session_token = build_signed_token(user_id, current_time)
    response.set_cookie(
        "session_token",
        session_token,
        httponly=True,
        secure=False,
        max_age=SESSION_LIFETIME_SECONDS,
    )
    return {"message": "Login successful", "session_token": session_token}


@app.get("/profile")
def profile(response: Response, session_token: str | None = Cookie(default=None)) -> dict[str, str]:
    if session_token is None:
        return unauthorized_response("Invalid session", response)

    try:
        user_id, last_activity = parse_signed_token(session_token)
    except ValueError as exc:
        return unauthorized_response(str(exc), response)

    profile_data = user_profiles.get(user_id)
    if profile_data is None:
        return unauthorized_response("Invalid session", response)

    current_time = int(time.time())
    elapsed = current_time - last_activity

    if elapsed < 0:
        return unauthorized_response("Invalid session", response)

    if elapsed >= SESSION_LIFETIME_SECONDS:
        return unauthorized_response("Session expired", response)

    if SESSION_REFRESH_THRESHOLD_SECONDS < elapsed < SESSION_LIFETIME_SECONDS:
        refreshed_token = build_signed_token(user_id, current_time)
        response.set_cookie(
            "session_token",
            refreshed_token,
            httponly=True,
            secure=False,
            max_age=SESSION_LIFETIME_SECONDS,
        )

    return {
        "user_id": user_id,
        "username": profile_data["username"],
        "full_name": profile_data["full_name"],
        "email": profile_data["email"],
    }
