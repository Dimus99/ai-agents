from __future__ import annotations

import functools
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class TechnicalPromptConfig(BaseModel):
    base_prompt: str
    rsi_length: int = 14
    macd: tuple[int, int, int] = (12, 26, 9)
    sma_fast: int = 50
    sma_slow: int = 200


class NewsPromptConfig(BaseModel):
    base_prompt: str


class PromptsConfig(BaseModel):
    technical: TechnicalPromptConfig
    news: NewsPromptConfig


@functools.lru_cache(maxsize=1)
def load_prompts(path: Optional[str] = None) -> PromptsConfig:
    config_path = Path(path or Path(__file__).resolve(
    ).parent.parent / "config" / "prompts.yaml")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    return PromptsConfig(**data["agents"])  # root key 'agents'
