# Задание 3.1

Запуск:

```bash
uvicorn main:app --reload
```

Пример запроса:

```http
POST /create_user
Content-Type: application/json

{
  "name": "Alice",
  "email": "alice@example.com",
  "age": 30,
  "is_subscribed": true
}
```
