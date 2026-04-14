# Задание 6.5

Запуск:

```bash
uvicorn main:app --reload
```

Регистрация:

```bash
curl -X POST http://127.0.0.1:8000/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}"
```

Логин:

```bash
curl -X POST http://127.0.0.1:8000/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"alice\",\"password\":\"qwerty123\"}"
```

Ограничения:

- `/register` - 1 запрос в минуту
- `/login` - 5 запросов в минуту
