from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.security.permissions import require_role
from app.models.generation import Generation
from app.models.spec import SpecSnapshot
from app.models.geometry import GeometryAsset
from app.schemas.factory_feedback import FactoryFeedbackIn, FactoryFeedbackOut
from app.geometry.service import ensure_geometry_assets

router = APIRouter(prefix="/projects/{project_id}/generations", tags=["factory_feedback"])


def _latest_specs(db: Session, generation_id: UUID) -> SpecSnapshot:
    snap = (
        db.query(SpecSnapshot)
        .filter(SpecSnapshot.generation_id == generation_id)
        .order_by(SpecSnapshot.created_at.desc())
        .first()
    )
    if not snap:
        raise HTTPException(status_code=404, detail="Spec snapshot not found for generation.")
    return snap


@router.post("/{generation_id}/factory-feedback", response_model=FactoryFeedbackOut)
def factory_feedback(
    project_id: UUID,
    generation_id: UUID,
    payload: FactoryFeedbackIn,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    """Create a new generation sourced from factory feedback.

    Why new generation?
    - Keeps lineage/audit clean (factory_feedback is a first-class generation source)
    - Avoids mutating historical generations used for prior exports
    """

    require_role(db, project_id, user.id, {"owner", "edit", "factory", "supplier", "qa"})

    base_gen = (
        db.query(Generation)
        .filter(Generation.id == generation_id, Generation.project_id == project_id)
        .one_or_none()
    )
    if not base_gen:
        raise HTTPException(status_code=404, detail="Base generation not found.")

    base_specs = _latest_specs(db, generation_id)

    # New generation derived from factory feedback
    new_gen = Generation(
        project_id=project_id,
        source="factory_feedback",
        parent_ids=[base_gen.id],
        is_active=False,
        created_by=user.id,
    )
    db.add(new_gen)
    db.commit()
    db.refresh(new_gen)

    # Copy specs forward (factory feedback is about geometry artifacts, not spec edits here)
    db.add(
        SpecSnapshot(
            generation_id=new_gen.id,
            instrumental_specs=base_specs.instrumental_specs,
            non_instrumental_specs=base_specs.non_instrumental_specs,
        )
    )

    if payload.make_active:
        db.execute(update(Generation).where(Generation.project_id == project_id).values(is_active=False))
        new_gen.is_active = True

    db.commit()
    db.refresh(new_gen)

    # Build deterministic geometry placeholders for the new generation.
    ga = ensure_geometry_assets(
        db,
        generation_id=new_gen.id,
        geom_version="factory_v1",
        geom_params={"from_generation": str(base_gen.id), "note": payload.message or ""},
    )

    # Apply factory-provided artifacts (if provided), while keeping our deterministic hash.
    if payload.mesh_uri is not None:
        ga.mesh_uri = payload.mesh_uri
    if payload.anchors_uri is not None:
        ga.anchors_uri = payload.anchors_uri
    if payload.bounds is not None:
        ga.bounds = payload.bounds

    db.add(ga)
    db.commit()
    db.refresh(ga)

    return FactoryFeedbackOut(
        created_generation_id=str(new_gen.id),
        geometry_hash=ga.geometry_hash,
        mesh_uri=ga.mesh_uri,
        anchors_uri=ga.anchors_uri,
        bounds=ga.bounds,
    )
