from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

from fastapi_limiter.depends import RateLimiter
from api.schemas.feedback import FeedbackIn
from api.deps import get_db
from api.security import require_api_key

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post(
    "/",
    dependencies=[Depends(require_api_key), Depends(RateLimiter(times=120, seconds=60))],
)
async def submit_feedback(feedback: FeedbackIn, db: AsyncSession = Depends(get_db)):
    data = feedback.dict()
    if data.get("metrics") is not None:
        data["metrics"] = json.dumps(data["metrics"])

    result = await db.execute(
        text("""
        INSERT INTO feedback (decision_id, outcome, metrics)
        VALUES (:decision_id, :outcome, :metrics)
        RETURNING feedback_id;
        """),
        data
    )
    await db.commit()
    return {"feedback_id": result.scalar()}
