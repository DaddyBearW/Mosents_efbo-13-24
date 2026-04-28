from typing import Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, conint, constr


app = FastAPI(title="Task 10.2")


class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = "Unknown"


class ValidationIssue(BaseModel):
    field: str
    message: str


class ValidationErrorResponse(BaseModel):
    error: str
    issues: list[ValidationIssue]


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exc: RequestValidationError) -> JSONResponse:
    issues: list[ValidationIssue] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"] if part != "body")
        issues.append(
            ValidationIssue(
                field=location or "body",
                message=error["msg"],
            )
        )

    return JSONResponse(
        status_code=422,
        content=ValidationErrorResponse(
            error="Validation failed",
            issues=issues,
        ).model_dump(),
    )


@app.post("/users")
def create_user(user: User) -> dict[str, object]:
    return {
        "message": "User data is valid",
        "user": user.model_dump(),
    }
