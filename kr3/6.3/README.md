# Задание 6.3

Файл `.env.example`:

```env
MODE=DEV
DOCS_USER=admin
DOCS_PASSWORD=12345
```

Запуск в DEV:

```bash
uvicorn main:app --reload
```

Проверка:

```bash
curl -u admin:12345 http://127.0.0.1:8000/docs
```

В режиме `PROD` эндпоинты `/docs`, `/openapi.json`, `/redoc` будут недоступны.
