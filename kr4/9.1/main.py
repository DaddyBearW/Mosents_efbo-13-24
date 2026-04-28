from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Product


app = FastAPI(title="Task 9.1")


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: float
    count: int
    description: str


@app.get("/products", response_model=list[ProductOut])
def list_products() -> list[Product]:
    with SessionLocal() as session:
        return session.scalars(select(Product).order_by(Product.id)).all()
