from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Agent, AgentRun, Round
from app.schemas.agent import AgentRead
from app.schemas.stats import StatsOverview, BestAgent, GenerationPnL
from app.orchestrator.evolution import run_round, evolve_agents


router = APIRouter()


@router.get("/agents", response_model=list[AgentRead])
async def api_agents(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Agent))
    return res.scalars().all()


@router.post("/agents/run")
async def api_run_all(db: AsyncSession = Depends(get_db)):
    await run_round(db, name="api")
    await db.commit()
    return {"status": "ok"}


@router.get("/agents/{agent_id}", response_model=AgentRead)
async def api_agent_details(agent_id: int, db: AsyncSession = Depends(get_db)):
    agent = await db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Agent not found")
    return agent


@router.post("/agents/evolve")
async def api_evolve(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Round).order_by(Round.id.desc()))
    last_round = res.scalars().first()
    if not last_round:
        raise HTTPException(400, "No rounds to evolve")
    await evolve_agents(db, last_round)
    await db.commit()
    return {"status": "ok"}


@router.get("/stats", response_model=StatsOverview)
async def api_stats(db: AsyncSession = Depends(get_db)):
    total_agents = (await db.execute(select(func.count(Agent.id)))).scalar() or 0
    active_agents = (
        await db.execute(select(func.count(Agent.id)).where(Agent.is_active == True))  # noqa: E712
    ).scalar() or 0
    total_rounds = (await db.execute(select(func.count(Round.id)))).scalar() or 0
    total_runs = (await db.execute(select(func.count(AgentRun.id)))).scalar() or 0

    best_row = (
        await db.execute(
            select(
                Agent.id, Agent.name, Agent.agent_type, Agent.generation, func.coalesce(
                    func.sum(AgentRun.pnl), 0.0)
            )
            .join(AgentRun, AgentRun.agent_id == Agent.id, isouter=True)
            .group_by(Agent.id)
            .order_by(func.coalesce(func.sum(AgentRun.pnl), 0.0).desc())
            .limit(1)
        )
    ).first()
    best_agent = None
    if best_row:
        best_agent = BestAgent(
            agent_id=best_row[0],
            name=best_row[1],
            agent_type=best_row[2],
            generation=best_row[3],
            total_pnl=float(best_row[4] or 0.0),
        )

    gen_rows = (
        await db.execute(
            select(Agent.generation, func.coalesce(
                func.sum(AgentRun.pnl), 0.0), func.count(Agent.id))
            .join(AgentRun, AgentRun.agent_id == Agent.id, isouter=True)
            .group_by(Agent.generation)
            .order_by(Agent.generation)
        )
    ).all()
    pnl_by_generation = [
        GenerationPnL(generation=int(r[0]), total_pnl=float(r[1] or 0.0), agents=int(r[2] or 0)) for r in gen_rows
    ]

    last_round_started_at = (await db.execute(select(Round.started_at).order_by(Round.id.desc()).limit(1))).scalar()

    return StatsOverview(
        total_agents=int(total_agents),
        active_agents=int(active_agents),
        total_rounds=int(total_rounds),
        total_runs=int(total_runs),
        best_agent=best_agent,
        pnl_by_generation=pnl_by_generation,
        last_round_started_at=last_round_started_at,
    )


@router.get("/status")
async def api_status(db: AsyncSession = Depends(get_db)):
    # Shows if there is an unfinished round and active worker heartbeat info could be added later
    running_round = (await db.execute(select(Round).where(Round.finished_at.is_(None)).order_by(Round.id.desc()))).scalars().first()
    return {
        "running": bool(running_round),
        "round": {
            "id": running_round.id,
            "name": running_round.name,
            "started_at": running_round.started_at,
        } if running_round else None,
    }


@router.get("/recent-runs")
async def api_recent_runs(limit: int = 50, db: AsyncSession = Depends(get_db)):
    q = (
        select(AgentRun.id, AgentRun.agent_id, AgentRun.round_id,
               AgentRun.signal, AgentRun.pnl, AgentRun.created_at, Agent.name)
        .join(Agent, Agent.id == AgentRun.agent_id)
        .order_by(AgentRun.id.desc())
        .limit(limit)
    )
    rows = (await db.execute(q)).all()
    return [
        {
            "id": r.id,
            "agent_id": r.agent_id,
            "agent_name": r.name,
            "round_id": r.round_id,
            "signal": r.signal,
            "pnl": r.pnl,
            "created_at": r.created_at,
        }
        for r in rows
    ]
