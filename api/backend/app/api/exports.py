from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.security.permissions import require_role
from app.models.generation import Generation
from app.models.export import ExportRecord, PROFILE_VALUES
from app.geometry.service import ensure_geometry_assets

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/projects/{project_id}/generations/{generation_id}")
def export_generation(
    project_id: UUID,
    generation_id: UUID,
    profile: str,
    formats: list[str],
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create an export record and return geometry payload.

    This is a deterministic placeholder export pipeline:
    - ensure geometry exists (mesh_uri/anchors_uri/bounds/hash)
    - create an exports row with a content-addressed export_uri
    - return export metadata
    """
    require_role(db, project_id, user.id, {"owner", "edit"})

    gen = (
        db.query(Generation)
        .filter(Generation.id == generation_id, Generation.project_id == project_id)
        .one_or_none()
    )
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found.")

    if profile not in PROFILE_VALUES:
        raise HTTPException(status_code=400, detail=f"Invalid profile. Use one of: {PROFILE_VALUES}")

    asset = ensure_geometry_assets(db, generation_id)

    export_uri = f"export://{profile}/{asset.geometry_hash}.zip"
    rec = ExportRecord(generation_id=generation_id, profile=profile, formats=formats, export_uri=export_uri)
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {
        "status": "created",
        "export_id": str(rec.id),
        "profile": rec.profile,
        "formats": rec.formats,
        "export_uri": rec.export_uri,
        "geometry": {
            "mesh_uri": asset.mesh_uri,
            "anchors_uri": asset.anchors_uri,
            "bounds": asset.bounds,
            "geometry_hash": asset.geometry_hash,
        },
    }
