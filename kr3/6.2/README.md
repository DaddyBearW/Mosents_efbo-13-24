# Задание 6.2

Запуск:

```bash
uvicorn main:app --reload
```

Регистрация:

```bash
curl -X POST http://127.0.0.1:8000/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"user1\",\"password\":\"correctpass\"}"
```

Логин:

```bash
curl -u user1:correctpass http://127.0.0.1:8000/login
```
