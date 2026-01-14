from fastapi import FastAPI
from redis.asyncio import Redis
from fastapi_limiter import FastAPILimiter

from api.config import settings
from api.routers import events, state, feedback, decide, ws

app = FastAPI(title="rr-engine API", version="1.1.0")

app.include_router(events.router)
app.include_router(state.router)
app.include_router(feedback.router)
app.include_router(decide.router)
app.include_router(ws.router)

@app.on_event("startup")
async def startup():
    redis = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
