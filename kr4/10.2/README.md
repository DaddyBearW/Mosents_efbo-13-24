# Task 10.2

Run:

```bash
py -3 -m uvicorn main:app --reload
```

Valid request:

```bash
curl -X POST http://127.0.0.1:8000/users ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"alice\",\"age\":21,\"email\":\"alice@example.com\",\"password\":\"superpass\",\"phone\":\"+79990000000\"}"
```

Invalid request:

```bash
curl -X POST http://127.0.0.1:8000/users ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"alice\",\"age\":16,\"email\":\"bad-email\",\"password\":\"123\"}"
```
