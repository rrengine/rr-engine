from pydantic import BaseModel, Field


class FactoryFeedbackIn(BaseModel):
    """Factory/supplier feedback that may update geometry artifacts."""

    mesh_uri: str | None = None
    anchors_uri: str | None = None
    bounds: dict | None = Field(default=None, description="{min:[x,y,z], max:[x,y,z], units:...}")
    message: str | None = None
    make_active: bool = True


class FactoryFeedbackOut(BaseModel):
    created_generation_id: str
    geometry_hash: str
    mesh_uri: str | None
    anchors_uri: str | None
    bounds: dict | None