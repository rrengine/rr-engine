from pydantic import BaseModel
from uuid import UUID

class ProjectCreate(BaseModel):
    name: str

class ProjectOut(BaseModel):
    id: UUID
    owner_id: UUID
    name: str

    class Config:
        from_attributes = True
