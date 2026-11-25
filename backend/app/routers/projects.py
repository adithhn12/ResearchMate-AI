from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Project, Paper, ActivityLog
from app.schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from app.auth import get_current_user
from app.services.vector_store import vector_store

router = APIRouter(prefix="/projects", tags=["Research Projects"])

@router.get("", response_model=List[ProjectResponse])
def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    results = []
    for p in projects:
        count = db.query(Paper).filter(Paper.project_id == p.id).count()
        p_res = ProjectResponse.from_orm(p)
        p_res.paper_count = count
        results.append(p_res)
    return results

@router.post("", response_model=ProjectResponse)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = Project(
        user_id=current_user.id,
        name=project_in.name,
        description=project_in.description
    )
    db.add(proj)
    db.commit()
    db.refresh(proj)

    log = ActivityLog(user_id=current_user.id, project_id=proj.id, action="create_project", details=f"Created project '{proj.name}'")
    db.add(log)
    db.commit()

    res = ProjectResponse.from_orm(proj)
    res.paper_count = 0
    return res

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    count = db.query(Paper).filter(Paper.project_id == proj.id).count()
    res = ProjectResponse.from_orm(proj)
    res.paper_count = count
    return res

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_in: ProjectUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    if project_in.name is not None:
        proj.name = project_in.name
    if project_in.description is not None:
        proj.description = project_in.description
    db.commit()
    db.refresh(proj)
    count = db.query(Paper).filter(Paper.project_id == proj.id).count()
    res = ProjectResponse.from_orm(proj)
    res.paper_count = count
    return res

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Delete vector store collection
    vector_store.delete_project_collection(project_id)

    # Clear project reference on activity logs to satisfy foreign key constraints
    db.query(ActivityLog).filter(ActivityLog.project_id == project_id).update(
        {"project_id": None}, synchronize_session=False
    )

    db.delete(proj)
    db.commit()
    return {"message": "Project deleted successfully"}
