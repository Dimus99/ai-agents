from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel


AgentType = Literal["technical", "news"]


class AgentBase(BaseModel):
    name: str
    agent_type: AgentType
    generation: int
    prompt: str
    is_active: bool = True


class AgentCreate(BaseModel):
    name: str
    agent_type: AgentType
    prompt: str
    generation: int = 0


class AgentRead(AgentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AgentUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None
    is_active: bool | None = None


class AgentRunRead(BaseModel):
    id: int
    agent_id: int
    round_id: int
    signal: Optional[str] = None
    pnl: float
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RoundRead(BaseModel):
    id: int
    name: str
    started_at: datetime
    finished_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    agent_id: int
    name: str
    agent_type: AgentType
    generation: int
    total_pnl: float
    runs: int


class RoundSummary(BaseModel):
    id: int
    name: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    runs: int
