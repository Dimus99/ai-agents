from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.agent import Agent, AgentRun, Round
from app.services.llm import LLMService
from app.agents.technical import TechnicalAgent, DEFAULT_TECH_PROMPT
from app.agents.news import NewsAgent, DEFAULT_NEWS_PROMPT


settings = get_settings()


@dataclass
class RuntimeAgent:
    model: Agent
    instance: Any


def instantiate_agent(agent: Agent) -> Any:
    if agent.agent_type == "technical":
        return TechnicalAgent(name=agent.name, prompt=agent.prompt)
    return NewsAgent(name=agent.name, prompt=agent.prompt)


async def ensure_initial_agents(db: AsyncSession) -> None:
    res = await db.execute(select(Agent))
    if res.scalars().first():
        return
    agents: list[Agent] = []
    for i in range(settings.initial_agents_per_type):
        agents.append(Agent(
            name=f"tech_{i}", agent_type="technical", generation=0, prompt=DEFAULT_TECH_PROMPT))
        agents.append(Agent(
            name=f"news_{i}", agent_type="news", generation=0, prompt=DEFAULT_NEWS_PROMPT))
    db.add_all(agents)
    await db.commit()


async def run_round(db: AsyncSession, name: str = "round") -> Round:
    await ensure_initial_agents(db)

    round_obj = Round(name=name)
    db.add(round_obj)
    await db.flush()

    agents = (await db.execute(select(Agent).where(Agent.is_active == True))).scalars().all()  # noqa: E712
    runtime_agents: list[RuntimeAgent] = [
        RuntimeAgent(a, instantiate_agent(a)) for a in agents]

    async def run_one(ra: RuntimeAgent) -> AgentRun:
        signal, details = await ra.instance.run()
        # PnL proxy: simplistic scoring
        pnl = 1.0 if signal == "buy" else (-1.0 if signal == "sell" else 0.0)
        ar = AgentRun(agent_id=ra.model.id, round_id=round_obj.id,
                      signal=signal, pnl=pnl, details=str(details))
        db.add(ar)
        return ar

    results = await asyncio.gather(*[run_one(ra) for ra in runtime_agents])
    await db.commit()

    await evolve_agents(db, round_obj)
    await db.commit()
    return round_obj


async def evolve_agents(db: AsyncSession, round_obj: Round) -> None:
    # Select best per type by last round pnl
    runs = (await db.execute(select(AgentRun).where(AgentRun.round_id == round_obj.id))).scalars().all()
    by_type: dict[str, list[tuple[AgentRun, Agent]]] = {
        "technical": [], "news": []}
    for r in runs:
        agent = await db.get(Agent, r.agent_id)
        if agent:
            by_type[agent.agent_type].append((r, agent))

    new_agents: list[Agent] = []
    llm = LLMService()
    for agent_type, tuples in by_type.items():
        tuples.sort(key=lambda t: t[0].pnl, reverse=True)
        elites = [t[1] for t in tuples[: settings.elite_per_type]]
        # keep elites
        for e in elites:
            e.is_active = True
        # deactivate others of this type
        for _, a in tuples[settings.elite_per_type:]:
            a.is_active = False

        # mutations
        for idx, base_agent in enumerate(elites[: settings.mutated_per_type]):
            description = f"Type: {agent_type}. Generation: {base_agent.generation}." \
                + " Goal: increase PnL with robust, low overfit rules."
            improved = await llm.mutate_prompt(description, base_agent.prompt)
            new_agents.append(
                Agent(
                    name=f"{agent_type}_mut_{base_agent.id}_{idx}",
                    agent_type=agent_type,
                    generation=base_agent.generation + 1,
                    prompt=improved,
                    is_active=True,
                )
            )

    db.add_all(new_agents)
