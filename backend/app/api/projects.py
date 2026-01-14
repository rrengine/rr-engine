from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.models.project import Project
from app.models.membership import ProjectMember
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    proj = Project(owner_id=user.id, name=payload.name)
    db.add(proj)
    db.commit()
    db.refresh(proj)

    db.add(ProjectMember(project_id=proj.id, user_id=user.id, role="owner"))
    db.commit()
    return proj

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Project).filter(Project.owner_id == user.id).all()
