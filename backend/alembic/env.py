from __future__ import annotations
from app.models.base import Base
from app.core.config import get_settings
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy import pool
from alembic import context

from logging.config import fileConfig
import os
import sys

# Ensure '/app' (project root in container) is on sys.path
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


from app.models.agent import Agent, AgentRun, Round  # noqa: F401


config = context.config
# Skip logging fileConfig to avoid missing logging sections

settings = get_settings()

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(settings.database_url.replace("+asyncpg", ""))

    with connectable.connect() as connection:
        context.configure(connection=connection,
                          target_metadata=target_metadata, compare_type=True)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
