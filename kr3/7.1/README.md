# Задание 7.1

Запуск:

```bash
uvicorn main:app --reload
```

Логин под администратором:

```bash
curl -X POST http://127.0.0.1:8000/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin1\",\"password\":\"admin123\"}"
```

Дальше используйте токен в заголовке `Authorization: Bearer TOKEN`.

Маршруты:

- `GET /protected_resource` - `admin`, `user`
- `POST /admin/resource` - только `admin`
- `PUT /user/resource` - `admin`, `user`
- `GET /guest/resource` - все роли
