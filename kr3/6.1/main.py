import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials


app = FastAPI(title="Task 6.1")
security = HTTPBasic()

VALID_USERNAME = "admin"
VALID_PASSWORD = "12345"


def check_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username_ok = secrets.compare_digest(credentials.username, VALID_USERNAME)
    password_ok = secrets.compare_digest(credentials.password, VALID_PASSWORD)

    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/login")
def login(_: str = Depends(check_credentials)) -> dict[str, str]:
    return {"message": "You got my secret, welcome"}
