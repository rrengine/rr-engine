from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api.deps import get_db, get_current_user
from app.models.spec import SpecSnapshot
from app.core.spec_validator import validate_specs
from app.schemas.validation import ValidationState

router = APIRouter(prefix="/generations", tags=["validation"])

@router.post("/{generation_id}/validate", response_model=ValidationState)
def validate_generation(generation_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    snap = db.query(SpecSnapshot).filter(SpecSnapshot.generation_id == generation_id).order_by(SpecSnapshot.created_at.desc()).first()
    if not snap:
        raise HTTPException(status_code=404, detail="Spec snapshot not found.")
    return validate_specs(snap.instrumental_specs, snap.non_instrumental_specs)
