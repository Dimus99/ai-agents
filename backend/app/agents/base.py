from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Literal


Signal = Literal["buy", "sell", "hold"]


class AgentBase(ABC):
    def __init__(self, name: str, prompt: str):
        self.name = name
        self.prompt = prompt

    @abstractmethod
    async def run(self) -> tuple[Signal, dict[str, Any]]:
        ...
