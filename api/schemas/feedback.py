from pydantic import BaseModel
from typing import Dict, Any, Optional

class FeedbackIn(BaseModel):
    decision_id: str
    outcome: str
    metrics: Optional[Dict[str, Any]] = None
