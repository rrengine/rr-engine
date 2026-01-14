from pydantic import BaseModel, Field
from typing import Literal, List
from uuid import UUID

GenerateMode = Literal["generate", "regenerate"]
UserChoice = Literal["1", "2", "3"]  # 1=AI Resolve Missing, 2=Cancel, 3=AI Draft

class GenerateRequest(BaseModel):
    base_generation_id: UUID
    mode: GenerateMode = "generate"
    choice: UserChoice = "2"
    make_active: bool = True

class GenerateResult(BaseModel):
    created_generation_id: UUID | None = None
    created_source: str | None = None
    ai_used: bool = False
    applied_defaults: List[str] = Field(default_factory=list)
    message: str
