import uuid

from fastapi import Cookie, FastAPI, HTTPException, Request, Response, status
from itsdangerous import BadSignature, Signer
from pydantic import BaseModel, ValidationError


app = FastAPI(title="Task 5.2")

SECRET_KEY = "super-secret-key-for-task-5-2"
signer = Signer(SECRET_KEY)

VALID_USERS = {
    "user123": {
        "password": "password123",
        "full_name": "Test User",
        "email": "user123@example.com",
    }
}
issued_tokens: dict[str, str] = {}


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

    user_id = str(uuid.uuid4())
    signed_token = signer.sign(user_id).decode()
    issued_tokens[signed_token] = data.username
    response.set_cookie("session_token", signed_token, httponly=True, max_age=1800)
    return {"message": "Login successful", "session_token": signed_token}


@app.get("/profile")
def profile(session_token: str | None = Cookie(default=None)) -> dict[str, str]:
    if session_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        user_id = signer.unsign(session_token).decode()
    except BadSignature as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized") from exc

    username = issued_tokens.get(session_token)
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user = VALID_USERS[username]
    return {
        "user_id": user_id,
        "username": username,
        "full_name": user["full_name"],
        "email": user["email"],
    }
