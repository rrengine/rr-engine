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

class GeometryAssetOut(BaseModel):
    id: UUID
    generation_id: UUID
    mesh_uri: str | None = None
    anchors_uri: str | None = None
    bounds: dict | None = None
    geometry_hash: str

    class Config:
        from_attributes = True


class GenerationOut(BaseModel):
    id: UUID
    project_id: UUID
    source: Source
    parent_ids: list[UUID] | None
    is_active: bool

    # Joined/embedded geometry view (may be None for legacy rows until ensured).
    geometry: GeometryAssetOut | None = None

    class Config:
        from_attributes = True
