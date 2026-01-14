from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

from fastapi_limiter.depends import RateLimiter
from api.schemas.state import StateSnapshotIn
from api.deps import get_db
from api.security import require_api_key

router = APIRouter(prefix="/state", tags=["state"])

@router.post(
    "/",
    dependencies=[Depends(require_api_key), Depends(RateLimiter(times=60, seconds=60))],
)
async def write_state(snapshot: StateSnapshotIn, db: AsyncSession = Depends(get_db)):
    data = snapshot.dict()
    data["state_data"] = json.dumps(data["state_data"])

    result = await db.execute(
        text("""
        INSERT INTO state_snapshots (system_id, context, state_data, confidence)
        VALUES (:system_id, :context, :state_data, :confidence)
        RETURNING snapshot_id;
        """),
        data
    )
    await db.commit()
    return {"snapshot_id": result.scalar()}
