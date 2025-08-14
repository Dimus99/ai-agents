AI Agents Orchestrator
======================

Стек: FastAPI (async), SQLAlchemy + Alembic, Celery + Redis, PostgreSQL, pandas/pandas-ta, httpx, Docker.

Структура проекта
-----------------

backend/app/{agents, orchestrator, services, routes, models, schemas, core}

Запуск
------

1) Установить Docker и Docker Compose.

2) Собрать и запустить:

```bash
docker-compose up --build
```

3) Выполнить миграции:

```bash
docker compose exec backend alembic upgrade head
```

4) Открыть Swagger: `http://localhost:8000/docs`.

.env
----

См. `backend/.env` (значения по умолчанию подготовлены для локального докера). При использовании OpenAI установите `LLM_PROVIDER=openai` и добавьте `OPENAI_API_KEY`.

API
---

- GET `/api/agents/` — список агентов
- GET `/api/agents/{id}/runs` — запуски агента
- POST `/api/orchestrator/run` — запуск торгового раунда (создание попыток и эволюция)

Команды Makefile (локально)
---------------------------

```bash
cd backend
make run
make migrate
```

Заметки
-------

- Эволюция: из каждого типа выбираются 2 лучших по PnL, создаются 2 мутировавших агента на их основе через LLM.
- PnL в демо считается по сигналу (buy=+1, sell=-1, hold=0) как заглушка. Замените на реальную логику исполнения/бумажной торговли.
- Технический агент использует RSI/MACD/SMA. Новостной агент агрегирует заголовки и использует LLM для тональности.
