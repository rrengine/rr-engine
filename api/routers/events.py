from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import json

from fastapi_limiter.depends import RateLimiter
from api.schemas.events import EventIn, EventBatchIn
from api.deps import get_db
from api.security import require_api_key
from api.services.betasphere import BetaSphere

router = APIRouter(prefix="/events", tags=["events"])

@router.post(
    "/",
    dependencies=[Depends(require_api_key), Depends(RateLimiter(times=120, seconds=60))],
)
async def ingest_event(event: EventIn, db: AsyncSession = Depends(get_db)):
    data = event.dict()
    data["payload"] = json.dumps(data["payload"])
    data["occurred_at"] = datetime.utcnow()

    result = await db.execute(
        text("""
        INSERT INTO events (system_id, module_id, event_type, payload, occurred_at)
        VALUES (:system_id, :module_id, :event_type, :payload, :occurred_at)
        RETURNING event_id;
        """),
        data
    )
    event_id = result.scalar()

    # 🔥 AUTO DECIDE
    bs = BetaSphere()
    decision = bs.decide(
        event_type=data["event_type"],
        payload=json.loads(data["payload"])
    )

    decision_data = {
        "system_id": data["system_id"],
        "trigger_event_id": event_id,
        "decision_type": decision["decision_type"],
        "decision_data": json.dumps(decision),
    }

    decision_result = await db.execute(
        text("""
        INSERT INTO decisions (system_id, trigger_event_id, decision_type, decision_data, executed)
        VALUES (:system_id, :trigger_event_id, :decision_type, :decision_data, FALSE)
        RETURNING decision_id;
        """),
        decision_data
    )

    await db.commit()

    return {
        "event_id": event_id,
        "decision_id": decision_result.scalar(),
        "decision": decision,
    }
