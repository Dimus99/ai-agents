from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Agent, AgentRun, Round
from app.schemas.agent import AgentRead, AgentRunRead, AgentCreate, AgentUpdate, LeaderboardEntry
from app.agents.technical import TechnicalAgent
from app.agents.news import NewsAgent


router = APIRouter()


@router.get("/", response_model=list[AgentRead])
async def list_agents(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Agent))
    return res.scalars().all()


@router.get("/{agent_id}/runs", response_model=list[AgentRunRead])
async def list_agent_runs(agent_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(AgentRun).where(AgentRun.agent_id == agent_id))
    return res.scalars().all()


@router.post("/{agent_id}/run", response_model=AgentRunRead)
async def run_single_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    instance = TechnicalAgent(agent.name, agent.prompt) if agent.agent_type == "technical" else NewsAgent(
        agent.name, agent.prompt)
    signal, details = await instance.run()
    # create ad-hoc round for this single run
    rnd = Round(name=f"single-{agent.id}")
    db.add(rnd)
    await db.flush()
    run = AgentRun(agent_id=agent.id, round_id=rnd.id,
                   signal=signal, pnl=0.0, details=str(details))
    db.add(run)
    await db.commit()
    await db.refresh(run)
    return run


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
async def create_agent(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    agent = Agent(
        name=payload.name,
        agent_type=payload.agent_type,
        prompt=payload.prompt,
        generation=payload.generation,
        is_active=True,
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.patch("/{agent_id}", response_model=AgentRead)
async def update_agent(agent_id: int, payload: AgentUpdate, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    if payload.name is not None:
        agent.name = payload.name
    if payload.prompt is not None:
        agent.prompt = payload.prompt
    if payload.is_active is not None:
        agent.is_active = payload.is_active
    await db.commit()
    await db.refresh(agent)
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        return
    await db.delete(agent)
    await db.commit()


@router.get("/leaderboard/top", response_model=list[LeaderboardEntry])
async def leaderboard(limit: int = 10, db: AsyncSession = Depends(get_db)):
    q = (
        select(
            Agent.id.label("agent_id"),
            Agent.name,
            Agent.agent_type,
            Agent.generation,
            func.coalesce(func.sum(AgentRun.pnl), 0.0).label("total_pnl"),
            func.count(AgentRun.id).label("runs"),
        )
        .join(AgentRun, AgentRun.agent_id == Agent.id, isouter=True)
        .group_by(Agent.id)
        .order_by(func.coalesce(func.sum(AgentRun.pnl), 0.0).desc())
        .limit(limit)
    )
    res = await db.execute(q)
    rows = res.all()
    return [
        LeaderboardEntry(
            agent_id=row.agent_id,
            name=row.name,
            agent_type=row.agent_type,
            generation=row.generation,
            total_pnl=float(row.total_pnl or 0.0),
            runs=int(row.runs or 0),
        )
        for row in rows
    ]
