from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel


class GenerationPnL(BaseModel):
    generation: int
    total_pnl: float
    agents: int


class BestAgent(BaseModel):
    agent_id: int
    name: str
    agent_type: str
    generation: int
    total_pnl: float


class StatsOverview(BaseModel):
    total_agents: int
    active_agents: int
    total_rounds: int
    total_runs: int
    best_agent: BestAgent | None
    pnl_by_generation: List[GenerationPnL]
    last_round_started_at: datetime | None
