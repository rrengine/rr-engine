from pydantic import BaseModel
from typing import Dict, Any, List

class EventIn(BaseModel):
    system_id: str
    module_id: str
    event_type: str
    payload: Dict[str, Any]

class EventBatchIn(BaseModel):
    events: List[EventIn]
