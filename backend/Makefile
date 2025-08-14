run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic upgrade head

revision:
	alembic revision -m "manual"

test:
	pytest -q


