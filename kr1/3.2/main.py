from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel


app = FastAPI(title="Task 3.2")


class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float


sample_products = [
    Product(product_id=123, name="Smartphone", category="Electronics", price=599.99),
    Product(product_id=456, name="Phone Case", category="Accessories", price=19.99),
    Product(product_id=789, name="Iphone", category="Electronics", price=1299.99),
    Product(product_id=101, name="Headphones", category="Accessories", price=99.99),
    Product(product_id=202, name="Smartwatch", category="Electronics", price=299.99),
]


@app.get("/products/search", response_model=list[Product])
def search_products(
    keyword: str = Query(..., min_length=1),
    category: Optional[str] = None,
    limit: int = Query(default=10, ge=1),
) -> list[Product]:
    keyword_lower = keyword.lower()

    results = [
        product
        for product in sample_products
        if keyword_lower in product.name.lower()
        and (category is None or product.category.lower() == category.lower())
    ]
    return results[:limit]


@app.get("/product/{product_id}", response_model=Product)
def get_product(product_id: int) -> Product:
    for product in sample_products:
        if product.product_id == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
