# Задание 6.4

Запуск:

```bash
uvicorn main:app --reload
```

Логин:

```bash
curl -X POST http://127.0.0.1:8000/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"john_doe\",\"password\":\"securepassword123\"}"
```

После этого возьмите `access_token` и передайте его в заголовке:

```bash
curl http://127.0.0.1:8000/protected_resource ^
  -H "Authorization: Bearer TOKEN"
```
