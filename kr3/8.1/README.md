# Задание 8.1

Сначала создайте таблицу:

```bash
py init_db.py
```

Потом запустите сервер:

```bash
uvicorn main:app --reload
```

Проверка:

```bash
curl -X POST http://127.0.0.1:8000/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"test_user\",\"password\":\"12345\"}"
```
