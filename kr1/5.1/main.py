import uuid

from fastapi import Cookie, FastAPI, HTTPException, Request, Response, status
from pydantic import BaseModel, ValidationError


app = FastAPI(title="Task 5.1")


VALID_USERS = {
    "user123": {
        "password": "password123",
        "full_name": "Test User",
        "email": "user123@example.com",
    }
}
active_sessions: dict[str, str] = {}


class LoginRequest(BaseModel):
    username: str
    password: str


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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    session_token = str(uuid.uuid4())
    active_sessions[session_token] = data.username
    response.set_cookie("session_token", session_token, httponly=True)
    return {"message": "Login successful", "session_token": session_token}


@app.get("/user")
def get_user(session_token: str | None = Cookie(default=None)) -> dict[str, str]:
    if session_token is None or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    username = active_sessions[session_token]
    user = VALID_USERS[username]
    return {
        "username": username,
        "full_name": user["full_name"],
        "email": user["email"],
    }
