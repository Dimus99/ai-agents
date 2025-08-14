from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.agent import Round
from app.schemas.agent import RoundRead, RoundSummary
from app.orchestrator.evolution import run_round, evolve_agents
from app.services.scheduler import run_round_task


router = APIRouter()


@router.post("/run", response_model=RoundRead)
async def run_once(db: AsyncSession = Depends(get_db)):
    round_obj: Round = await run_round(db, name="manual")
    return round_obj


@router.post("/schedule/trigger")
async def trigger_async_round():
    run_round_task.delay()
    return {"status": "queued"}


@router.post("/evolve", response_model=RoundRead)
async def force_evolve(round_id: int | None = None, db: AsyncSession = Depends(get_db)):
    if round_id is None:
        res = await db.execute(select(Round).order_by(Round.id.desc()))
        round_obj = res.scalars().first()
        if not round_obj:
            raise HTTPException(status_code=400, detail="No rounds to evolve")
    else:
        round_obj = await db.get(Round, round_id)
        if not round_obj:
            raise HTTPException(status_code=404, detail="Round not found")
    await evolve_agents(db, round_obj)
    await db.commit()
    return round_obj


@router.get("/rounds", response_model=list[RoundSummary])
async def list_rounds(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select, func
    from app.models.agent import AgentRun

    res = await db.execute(select(Round))
    rounds = res.scalars().all()
    summaries: list[RoundSummary] = []
    for r in rounds:
        count = (await db.execute(select(func.count(AgentRun.id)).where(AgentRun.round_id == r.id))).scalar() or 0
        summaries.append(RoundSummary(
            id=r.id, name=r.name, started_at=r.started_at, finished_at=r.finished_at, runs=int(count)))
    return summaries
