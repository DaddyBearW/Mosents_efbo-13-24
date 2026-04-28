# Task 10.1

Run:

```bash
py -3 -m uvicorn main:app --reload
```

Trigger the first custom error:

```bash
curl http://127.0.0.1:8000/check-number/-3
```

Trigger the second custom error:

```bash
curl http://127.0.0.1:8000/products/99
```
