from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.security.permissions import require_role
from app.models.generation import Generation
from app.models.spec import SpecSnapshot
from app.models.geometry import GeometryAsset
from app.geometry.service import ensure_geometry_assets


router = APIRouter(prefix="/projects/{project_id}/generations", tags=["factory_feedback"])


class FactoryFeedbackIn(BaseModel):
    """Factory/supplier feedback that may include real geometry outputs."""
    mesh_uri: str | None = None
    anchors_uri: str | None = None
    bounds: dict | None = None


@router.post("/{generation_id}/factory-feedback")
def create_factory_feedback_generation(
    project_id: UUID,
    generation_id: UUID,
    payload: FactoryFeedbackIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    require_role(db, project_id, user.id, {"owner", "edit", "factory", "supplier"})

    base_gen = (
        db.query(Generation)
        .filter(Generation.id == generation_id, Generation.project_id == project_id)
        .one_or_none()
    )
    if not base_gen:
        raise HTTPException(status_code=404, detail="Generation not found.")

    base_specs = (
        db.query(SpecSnapshot)
        .filter(SpecSnapshot.generation_id == base_gen.id)
        .order_by(SpecSnapshot.created_at.desc())
        .first()
    )
    if not base_specs:
        raise HTTPException(status_code=404, detail="Spec snapshot not found for generation.")

    # Create a new generation to preserve lineage/auditability.
    fb_gen = Generation(
        project_id=project_id,
        source="factory_feedback",
        parent_ids=[base_gen.id],
        is_active=False,
        created_by=user.id,
    )
    db.add(fb_gen)
    db.commit()
    db.refresh(fb_gen)

    # Copy specs forward (factory feedback typically addresses manufacturability, not user intent).
    db.add(
        SpecSnapshot(
            generation_id=fb_gen.id,
            instrumental_specs=base_specs.instrumental_specs,
            non_instrumental_specs=base_specs.non_instrumental_specs,
        )
    )
    db.commit()

    # Ensure deterministic geometry for the new generation.
    asset = ensure_geometry_assets(db, fb_gen.id, geom_version="factory_v1")

    # If factory provided real outputs, attach them while keeping geometry_hash.
    if payload.mesh_uri is not None:
        asset.mesh_uri = payload.mesh_uri
    if payload.anchors_uri is not None:
        asset.anchors_uri = payload.anchors_uri
    if payload.bounds is not None:
        asset.bounds = payload.bounds
    db.add(asset)
    db.commit()
    db.refresh(asset)

    return {
        "generation_id": str(fb_gen.id),
        "source": fb_gen.source,
        "parent_ids": [str(base_gen.id)],
        "geometry": {
            "mesh_uri": asset.mesh_uri,
            "anchors_uri": asset.anchors_uri,
            "bounds": asset.bounds,
            "geometry_hash": asset.geometry_hash,
        },
    }
