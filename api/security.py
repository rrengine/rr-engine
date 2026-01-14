from fastapi import Header, HTTPException
from api.config import settings

async def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not x_api_key or x_api_key not in settings.api_key_set():
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key
