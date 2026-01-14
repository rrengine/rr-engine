from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.models.generation import Generation
from app.models.geometry import GeometryAsset
from app.security.permissions import require_role

router = APIRouter(prefix="/import", tags=["import"])

@router.post("/projects/{project_id}")
def import_geometry(project_id: UUID, mesh_uri: str, anchors_uri: str | None = None, geometry_hash: str | None = None,
                   db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_role(db, project_id, user.id, {"owner","edit"})
    gen = Generation(project_id=project_id, source="import", parent_ids=None, is_active=False, created_by=user.id)
    db.add(gen)
    db.commit()
    db.refresh(gen)

    if not geometry_hash:
        geometry_hash = "imported_" + str(gen.id)

    asset = GeometryAsset(generation_id=gen.id, mesh_uri=mesh_uri, anchors_uri=anchors_uri, bounds=None, geometry_hash=geometry_hash)
    db.add(asset)

    # imported generations can be set active if desired in client flow; keep inactive by default
    db.commit()
    return {"generation_id": str(gen.id), "geometry_hash": geometry_hash}
