from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.generation import Generation
from app.models.spec import SpecSnapshot
from app.models.ai_actions import AIAction
from app.schemas.generate import GenerateRequest, GenerateResult
from app.core.spec_validator import validate_specs
from app.core.non_instrumental_resolver import (
    apply_canonical_defaults_for_missing,
    create_ai_draft_non_instrumental,
)
from app.geometry.service import ensure_geometry_assets

router = APIRouter(prefix="/generate", tags=["generate"])

def _latest_specs(db: Session, generation_id: UUID) -> SpecSnapshot:
    snap = db.query(SpecSnapshot).filter(SpecSnapshot.generation_id == generation_id).order_by(SpecSnapshot.created_at.desc()).first()
    if not snap:
        raise HTTPException(status_code=404, detail="Spec snapshot not found for generation.")
    return snap

@router.post("", response_model=GenerateResult)
def generate(payload: GenerateRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    base_gen = db.query(Generation).filter(Generation.id == payload.base_generation_id).one_or_none()
    if not base_gen:
        raise HTTPException(status_code=404, detail="Base generation not found.")

    base_specs = _latest_specs(db, base_gen.id)
    state = validate_specs(base_specs.instrumental_specs, base_specs.non_instrumental_specs)

    if state.is_blocking:
        raise HTTPException(status_code=400, detail={
            "message": "Blocking instrumental spec errors. Fix before generation.",
            "validation": state.model_dump(),
        })

    applied = []
    ai_used = False
    created_source = "regenerate" if payload.mode == "regenerate" else "generate"
    updated_non_inst = base_specs.non_instrumental_specs

    if state.missing_non_instrumental:
        if payload.choice == "2":
            return GenerateResult(
                created_generation_id=None,
                created_source=None,
                ai_used=False,
                applied_defaults=[],
                message=f"Generation cancelled. Missing {len(state.missing_non_instrumental)} non-instrumental fields.",
            )

        if payload.choice == "1":
            updated_non_inst, applied = apply_canonical_defaults_for_missing(base_specs.non_instrumental_specs)
            ai_used = True
            created_source = "generate" if payload.mode == "generate" else "regenerate"
            db.add(AIAction(generation_id=base_gen.id, mode="resolve", fields_modified=applied, invoked_by=user.id))

        elif payload.choice == "3":
            updated_non_inst, applied = create_ai_draft_non_instrumental(base_specs.non_instrumental_specs)
            ai_used = True
            created_source = "ai_draft"
            db.add(AIAction(generation_id=base_gen.id, mode="draft", fields_modified=applied, invoked_by=user.id))
        else:
            raise HTTPException(status_code=400, detail="Invalid choice. Use '1', '2', or '3'.")

    new_gen = Generation(
        project_id=base_gen.project_id,
        source=created_source,
        parent_ids=[base_gen.id],
        is_active=False,
        created_by=user.id,
    )
    db.add(new_gen)
    db.commit()
    db.refresh(new_gen)

    db.add(SpecSnapshot(
        generation_id=new_gen.id,
        instrumental_specs=base_specs.instrumental_specs,
        non_instrumental_specs=updated_non_inst,
    ))

    if payload.make_active:
        db.execute(update(Generation).where(Generation.project_id == base_gen.project_id).values(is_active=False))
        new_gen.is_active = True

    db.commit()
    db.refresh(new_gen)

    # Step 3/4+: deterministically build geometry placeholders + reproducibility key.
    # Must run AFTER the spec snapshot is persisted.
    ensure_geometry_assets(db, generation_id=new_gen.id, geom_version="stub_v1")

    return GenerateResult(
        created_generation_id=new_gen.id,
        created_source=created_source,
        ai_used=ai_used,
        applied_defaults=applied,
        message="Generation created. Geometry placeholders + deterministic geometry_hash created.",
    )
