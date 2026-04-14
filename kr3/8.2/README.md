# Задание 8.2

Запуск:

```bash
uvicorn main:app --reload
```

Создание:

```bash
curl -X POST http://127.0.0.1:8000/todos ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\"}"
```

Получение:

```bash
curl http://127.0.0.1:8000/todos/1
```

Обновление:

```bash
curl -X PUT http://127.0.0.1:8000/todos/1 ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Buy groceries\",\"description\":\"Milk, eggs, bread\",\"completed\":true}"
```

Удаление:

```bash
curl -X DELETE http://127.0.0.1:8000/todos/1
```
