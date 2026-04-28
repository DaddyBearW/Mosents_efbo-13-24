# Task 9.1

Apply the first migration:

```bash
py -3 -m alembic upgrade 0001_create_products
```

Insert two rows into the initial schema:

```bash
py seed_products.py
```

Apply the second migration:

```bash
py -3 -m alembic upgrade head
```

Run the app:

```bash
py -3 -m uvicorn main:app --reload
```

Check products:

```bash
curl http://127.0.0.1:8000/products
```
