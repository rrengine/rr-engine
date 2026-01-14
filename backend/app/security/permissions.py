from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.membership import ProjectMember

def require_role(db: Session, project_id: UUID, user_id: UUID, allowed_roles: set[str]):
    m = (
        db.query(ProjectMember)
        .filter(ProjectMember.project_id == project_id, ProjectMember.user_id == user_id)
        .one_or_none()
    )
    if not m or m.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient role.")
    if m.expires_at is not None:
        now = datetime.now(timezone.utc)
        if m.expires_at < now:
            raise HTTPException(status_code=403, detail="Access expired.")
    return m
