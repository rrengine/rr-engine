from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.api.deps import get_db, get_current_user
from app.security.permissions import require_role
from app.geometry.service import ensure_geometry_assets
from app.models.generation import Generation
from app.models.export import ExportRecord, PROFILE_VALUES

router = APIRouter(prefix="/export", tags=["export"])

@router.post("/projects/{project_id}/generations/{generation_id}")
def export_generation(project_id: UUID, generation_id: UUID, profile: str, formats: list[str],
                      db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_role(db, project_id, user.id, {"owner","edit"})
    if profile not in PROFILE_VALUES:
        raise HTTPException(status_code=400, detail=f"Invalid profile. Use one of: {list(PROFILE_VALUES)}")

    gen = db.query(Generation).filter(Generation.id == generation_id, Generation.project_id == project_id).one_or_none()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found.")

    # Step 6: export consumes geometry_assets (ensures deterministic placeholders exist).
    ga = ensure_geometry_assets(db, generation_id=generation_id, geom_version="stub_v1")

    # Skeleton export URI (content-addressed). Replace later with real zip/build pipeline.
    export_uri = f"export://{profile}/{ga.geometry_hash}/bundle.zip"
    rec = ExportRecord(generation_id=generation_id, profile=profile, formats=formats, export_uri=export_uri)
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {
        "status": "created",
        "profile": profile,
        "formats": formats,
        "generation_id": str(generation_id),
        "geometry": {
            "mesh_uri": ga.mesh_uri,
            "anchors_uri": ga.anchors_uri,
            "bounds": ga.bounds,
            "geometry_hash": ga.geometry_hash,
        },
        "export_uri": rec.export_uri,
        "export_id": str(rec.id),
    }
