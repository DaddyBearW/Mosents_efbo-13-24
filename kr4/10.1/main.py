from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel


app = FastAPI(title="Task 10.1")

PRODUCTS = {
    1: {"id": 1, "title": "Keyboard", "price": 2499},
    2: {"id": 2, "title": "Mouse", "price": 1499},
}


class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int


class InvalidNumberException(Exception):
    def __init__(self, value: int) -> None:
        self.status_code = 400
        self.message = f"Value must be positive. Received: {value}"


class ProductNotFoundException(Exception):
    def __init__(self, product_id: int) -> None:
        self.status_code = 404
        self.message = f"Product with id={product_id} was not found"


@app.exception_handler(InvalidNumberException)
async def invalid_number_handler(_, exc: InvalidNumberException) -> JSONResponse:
    print(f"Invalid number error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="InvalidNumberException",
            message=exc.message,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.exception_handler(ProductNotFoundException)
async def product_not_found_handler(_, exc: ProductNotFoundException) -> JSONResponse:
    print(f"Product lookup error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="ProductNotFoundException",
            message=exc.message,
            status_code=exc.status_code,
        ).model_dump(),
    )


@app.get("/check-number/{value}")
def check_number(value: int) -> dict[str, int | str]:
    if value <= 0:
        raise InvalidNumberException(value)
    return {"message": "Value is valid", "value": value}


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict[str, int | str]:
    product = PRODUCTS.get(product_id)
    if product is None:
        raise ProductNotFoundException(product_id)
    return product
