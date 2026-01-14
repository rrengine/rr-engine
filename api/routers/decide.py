from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

from fastapi_limiter.depends import RateLimiter
from api.deps import get_db
from api.security import require_api_key
from api.services.betasphere import BetaSphere

router = APIRouter(prefix="/decide", tags=["decide"])

@router.post(
    "/{event_id}",
    dependencies=[Depends(require_api_key), Depends(RateLimiter(times=30, seconds=60))],
)
async def decide_from_event(event_id: str, db: AsyncSession = Depends(get_db)):
    r = await db.execute(
        text("""
        SELECT system_id, event_type, payload
        FROM events
        WHERE event_id = :event_id
        LIMIT 1;
        """),
        {"event_id": event_id}
    )
    row = r.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="event_id not found")

    system_id, event_type, payload = row

    bs = BetaSphere()
    decision = bs.decide(event_type=event_type, payload=payload)

    data = {
        "system_id": system_id,
        "trigger_event_id": event_id,
        "decision_type": decision["decision_type"],
        "decision_data": json.dumps(decision)
    }

    ins = await db.execute(
        text("""
        INSERT INTO decisions (system_id, trigger_event_id, decision_type, decision_data, executed)
        VALUES (:system_id, :trigger_event_id, :decision_type, :decision_data, FALSE)
        RETURNING decision_id;
        """),
        data
    )
    await db.commit()

    return {"decision_id": ins.scalar(), "decision": decision}
