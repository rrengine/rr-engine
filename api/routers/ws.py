import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from api.deps import get_db
from api.config import settings

router = APIRouter(tags=["ws"])

@router.websocket("/ws/state/{system_id}")
async def ws_state(websocket: WebSocket, system_id: str):
    api_key = websocket.headers.get("x-api-key")
    if not api_key or api_key not in settings.api_key_set():
        await websocket.close(code=1008)
        return

    await websocket.accept()

    async for db in get_db():
        last_snapshot_id = None
        try:
            while True:
                r = await db.execute(
                    text("""
                    SELECT snapshot_id, state_data, confidence, created_at
                    FROM state_snapshots
                    WHERE system_id = :system_id
                    ORDER BY created_at DESC
                    LIMIT 1;
                    """),
                    {"system_id": system_id}
                )
                row = r.fetchone()
                if row:
                    snapshot_id, state_data, confidence, created_at = row
                    if snapshot_id != last_snapshot_id:
                        last_snapshot_id = snapshot_id
                        await websocket.send_json({
                            "snapshot_id": snapshot_id,
                            "state": state_data,
                            "confidence": confidence,
                            "timestamp": created_at.isoformat()
                        })
                await asyncio.sleep(1)
        except WebSocketDisconnect:
            return
