from __future__ import annotations

import asyncio

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings


settings = get_settings()

celery_app = Celery(
    "agents",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


def _parse_cron(cron: str):
    parts = cron.strip().split()
    if len(parts) != 5:
        return crontab(minute="*/15")
    minute, hour, day_of_month, month, day_of_week = parts
    return crontab(minute=minute, hour=hour, day_of_month=day_of_month, month_of_year=month, day_of_week=day_of_week)


celery_app.conf.beat_schedule = {
    "scheduled-round": {
        "task": "app.services.scheduler.run_round_task",
        "schedule": _parse_cron(settings.schedule_cron),
        "options": {"expires": 60 * 10},
    }
} if settings.scheduler_enabled else {}


@celery_app.task
def run_round_task():
    # Delayed import to avoid heavy deps in worker init
    import anyio
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.db.session import AsyncSessionLocal
    from app.orchestrator.evolution import run_round

    async def _run():
        async with AsyncSessionLocal() as session:  # type: AsyncSession
            await run_round(session, name="scheduled")

    anyio.run(_run)
