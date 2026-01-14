from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.generation import Generation
from app.models.spec import SpecSnapshot
from app.schemas.generation import GenerationCreate, GenerationOut
from app.security.permissions import require_role
from app.geometry.service import ensure_geometry_assets

router = APIRouter(prefix="/projects/{project_id}/generations", tags=["generations"])

@router.post("", response_model=GenerationOut)
def create_generation(project_id: UUID, payload: GenerationCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id).one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found.")

    require_role(db, project_id, user.id, {"owner","edit"})

    gen = Generation(project_id=project_id, source=payload.source, parent_ids=payload.parent_ids, is_active=False, created_by=user.id)
    db.add(gen)
    db.commit()
    db.refresh(gen)

    snap = SpecSnapshot(generation_id=gen.id, instrumental_specs=payload.instrumental_specs, non_instrumental_specs=payload.non_instrumental_specs)
    db.add(snap)

    if payload.make_active:
        db.execute(update(Generation).where(Generation.project_id == project_id).values(is_active=False))
        gen.is_active = True

    db.commit()
    db.refresh(gen)

    # Step 3/4+: deterministically build geometry placeholders + reproducibility key.
    ensure_geometry_assets(db, generation_id=gen.id, geom_version="stub_v1")
    return gen

@router.get("", response_model=list[GenerationOut])
def list_generations(project_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_role(db, project_id, user.id, {"owner","edit","view","factory","supplier","render","qa"})
    return db.query(Generation).filter(Generation.project_id == project_id).order_by(Generation.created_at.desc()).all()

@router.post("/{generation_id}/set-active", response_model=GenerationOut)
def set_active(project_id: UUID, generation_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    require_role(db, project_id, user.id, {"owner","edit"})
    gen = db.query(Generation).filter(Generation.id == generation_id, Generation.project_id == project_id).one_or_none()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found.")
    db.execute(update(Generation).where(Generation.project_id == project_id).values(is_active=False))
    gen.is_active = True
    db.commit()
    db.refresh(gen)
    return gen
