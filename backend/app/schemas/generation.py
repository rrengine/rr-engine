from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal

Source = Literal["generate","regenerate","import","ai_merge","ai_draft","factory_feedback"]

class GenerationCreate(BaseModel):
    source: Source = "generate"
    parent_ids: list[UUID] | None = None
    instrumental_specs: dict = Field(default_factory=dict)
    non_instrumental_specs: dict | None = None
    make_active: bool = True

class GenerationOut(BaseModel):
    id: UUID
    project_id: UUID
    source: Source
    parent_ids: list[UUID] | None
    is_active: bool

    class Config:
        from_attributes = True
