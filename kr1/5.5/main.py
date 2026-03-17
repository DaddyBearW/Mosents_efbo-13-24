import re
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from pydantic import BaseModel, Field, ValidationError, field_validator


app = FastAPI(title="Task 5.5")

ACCEPT_LANGUAGE_PATTERN = re.compile(
    r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,3})?(?:,[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,3})?(?:;q=(?:0(?:\.\d+)?|1(?:\.0+)?))?)*$"
)


class CommonHeaders(BaseModel):
    user_agent: str = Field(..., min_length=1)
    accept_language: str = Field(..., min_length=1)

    @field_validator("user_agent", "accept_language", mode="before")
    @classmethod
    def strip_value(cls, value: str) -> str:
        return value.strip()

    @field_validator("accept_language")
    @classmethod
    def validate_accept_language(cls, value: str) -> str:
        normalized = value.replace(" ", "")
        if not ACCEPT_LANGUAGE_PATTERN.fullmatch(normalized):
            raise ValueError("Invalid Accept-Language format")
        return normalized


def get_common_headers(
    user_agent: Annotated[str | None, Header()] = None,
    accept_language: Annotated[str | None, Header()] = None,
) -> CommonHeaders:
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Required headers are missing")

    try:
        return CommonHeaders(user_agent=user_agent, accept_language=accept_language)
    except ValidationError as exc:
        message = exc.errors()[0]["msg"]
        raise HTTPException(status_code=400, detail=message) from exc


@app.get("/headers")
def read_headers(headers: Annotated[CommonHeaders, Depends(get_common_headers)]) -> dict[str, str]:
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language,
    }


@app.get("/info")
def info(
    response: Response,
    headers: Annotated[CommonHeaders, Depends(get_common_headers)],
) -> dict[str, object]:
    response.headers["X-Server-Time"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language,
        },
    }
