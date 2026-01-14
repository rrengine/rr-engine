from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from uuid import UUID

class StateSnapshotIn(BaseModel):
    system_id: UUID
    context: str
    state_data: Dict[str, Any]
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
