from datetime import datetime
from typing import Optional, Literal

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


AgentType = Literal["technical", "news"]


class Agent(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_type: Mapped[str] = mapped_column(
        String(32), nullable=False)  # technical | news
    generation: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    runs: Mapped[list[AgentRun]] = relationship(
        "AgentRun", back_populates="agent")  # type: ignore[name-defined]


class AgentRun(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(
        ForeignKey("agent.id", ondelete="CASCADE"))
    round_id: Mapped[int] = mapped_column(
        ForeignKey("round.id", ondelete="CASCADE"))
    signal: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    pnl: Mapped[float] = mapped_column(Float, default=0.0)
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    agent: Mapped[Agent] = relationship(
        "Agent", back_populates="runs")  # type: ignore[name-defined]
    round: Mapped["Round"] = relationship(
        "Round", back_populates="runs")  # type: ignore[name-defined]


class Round(Base):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]
                        ] = mapped_column(DateTime, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    runs: Mapped[list[AgentRun]] = relationship(
        "AgentRun", back_populates="round")  # type: ignore[name-defined]
