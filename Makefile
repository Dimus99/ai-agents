run:
	docker-compose up --build

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -q || true


