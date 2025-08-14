run:
	docker-compose up --build

migrate:
	docker compose exec backend alembic upgrade head

test:
	docker compose exec backend pytest -q || true

dev:
	docker-compose up --build frontend backend db redis worker beat

build:
	docker-compose build

start:
	docker-compose up -d


