# Задание 6.3

Файл `.env.example`:

```env
MODE=DEV
DOCS_USER=admin
DOCS_PASSWORD=12345
```

Запуск в `DEV`:

```bash
uvicorn main:app --reload
```

Проверка в `DEV`:

```bash
curl -u admin:12345 http://127.0.0.1:8000/docs
curl -u admin:12345 http://127.0.0.1:8000/openapi.json
curl http://127.0.0.1:8000/redoc
```

Запуск в `PROD`:

```bash
set MODE=PROD
uvicorn main:app --reload
```

Проверка в `PROD`:

```bash
curl http://127.0.0.1:8000/docs
curl http://127.0.0.1:8000/openapi.json
curl http://127.0.0.1:8000/redoc
```

В `DEV` эндпоинты `/docs` и `/openapi.json` доступны только по Basic Auth.
В `PROD` эндпоинты `/docs`, `/openapi.json` и `/redoc` принудительно возвращают `404 Not Found`.
