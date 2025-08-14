FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

WORKDIR /app
COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-dev --no-interaction --no-ansi

COPY app /app/app
COPY alembic /app/alembic
COPY alembic.ini /app/

EXPOSE 8000


