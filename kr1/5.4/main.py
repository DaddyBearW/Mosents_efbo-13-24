import re

from fastapi import FastAPI, Header, HTTPException


app = FastAPI(title="Task 5.4")

ACCEPT_LANGUAGE_PATTERN = re.compile(
    r"^[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,3})?(?:,[a-zA-Z]{2,3}(?:-[a-zA-Z]{2,3})?(?:;q=(?:0(?:\.\d+)?|1(?:\.0+)?))?)*$"
)


@app.get("/headers")
def read_headers(
    user_agent: str | None = Header(default=None),
    accept_language: str | None = Header(default=None),
) -> dict[str, str]:
    if not user_agent or not accept_language:
        raise HTTPException(status_code=400, detail="Required headers are missing")

    normalized_accept_language = accept_language.replace(" ", "")
    if not ACCEPT_LANGUAGE_PATTERN.fullmatch(normalized_accept_language):
        raise HTTPException(status_code=400, detail="Invalid Accept-Language format")

    return {
        "User-Agent": user_agent,
        "Accept-Language": normalized_accept_language,
    }
