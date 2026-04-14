import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials


load_dotenv()

MODE = os.getenv("MODE", "DEV").upper()
DOCS_USER = os.getenv("DOCS_USER", "admin")
DOCS_PASSWORD = os.getenv("DOCS_PASSWORD", "12345")

if MODE not in {"DEV", "PROD"}:
    raise ValueError("MODE must be DEV or PROD")


app = FastAPI(
    title="Task 6.3",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
security = HTTPBasic()


def check_docs_auth(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    username_ok = secrets.compare_digest(credentials.username, DOCS_USER)
    password_ok = secrets.compare_digest(credentials.password, DOCS_PASSWORD)

    if not username_ok or not password_ok:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect docs username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


@app.get("/ping")
def ping() -> dict[str, str]:
    return {"message": "pong", "mode": MODE}


if MODE == "DEV":
    @app.get("/openapi.json", include_in_schema=False)
    def openapi_json(_: str = Depends(check_docs_auth)) -> JSONResponse:
        return JSONResponse(app.openapi())


    @app.get("/docs", include_in_schema=False)
    def custom_swagger(_: str = Depends(check_docs_auth)):
        return get_swagger_ui_html(openapi_url="/openapi.json", title=app.title + " Docs")
