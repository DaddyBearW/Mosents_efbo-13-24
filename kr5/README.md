# KR5


## Запуск локально

```bash
python -m venv .venv
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest
```

## Docker

```bash
docker compose up --build
```
