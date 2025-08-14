from functools import lru_cache
from typing import Literal, Optional

from pydantic import BaseSettings, Field, AnyUrl


class Settings(BaseSettings):
    # App
    app_name: str = Field(default="AI Agents Orchestrator")
    env: Literal["local", "dev", "prod"] = Field(default="local")
    debug: bool = Field(default=True)

    # Networking
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@db:5432/agents"
    )

    # Redis / Celery
    redis_url: str = Field(default="redis://redis:6379/0")
    celery_broker_url: str = Field(default="redis://redis:6379/1")
    celery_result_backend: str = Field(default="redis://redis:6379/2")

    # Bybit
    bybit_base_url: AnyUrl = Field(default="https://api-testnet.bybit.com")
    bybit_symbol: str = Field(default="BTCUSDT")
    # minutes: 1,3,5,15,30,60,120,240,360,720,D,W,M
    bybit_interval: str = Field(default="15")
    bybit_lookback_candles: int = Field(default=200)

    # LLM
    llm_provider: Literal["openai", "ollama"] = Field(default="openai")
    openai_api_key: Optional[str] = Field(default=None)
    openai_base_url: Optional[str] = Field(default=None)
    openai_model: str = Field(default="gpt-4o-mini")
    ollama_base_url: str = Field(default="http://host.docker.internal:11434")
    ollama_model: str = Field(default="mistral")

    # Agents / Orchestration
    initial_agents_per_type: int = Field(default=4)
    elite_per_type: int = Field(default=2)
    mutated_per_type: int = Field(default=2)
    use_paper_trading: bool = Field(default=True)

    # Scheduler
    schedule_cron: str = Field(default="*/15 * * * *")  # every 15 minutes
    scheduler_enabled: bool = Field(default=True)

    # Logging
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True)

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
