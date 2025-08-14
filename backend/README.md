Запуск локально (без Docker)
----------------------------

```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs


