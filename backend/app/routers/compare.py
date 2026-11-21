import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Paper, PaperChunk, PaperComparison, ActivityLog
from app.schemas import ComparisonRequest, ComparisonResponse, ComparisonItem
from app.auth import get_current_user
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/compare", tags=["Research Paper Comparison"])

@router.post("/generate", response_model=ComparisonResponse)
def generate_comparison(
    req: ComparisonRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if len(req.paper_ids) < 2:
        raise HTTPException(status_code=400, detail="Please select at least 2 research papers to compare")

    papers = db.query(Paper).filter(Paper.id.in_(req.paper_ids), Paper.project_id == req.project_id).all()
    if len(papers) < 2:
        raise HTTPException(status_code=400, detail="Could not find the specified papers in this project")

    # Gather content samples for each paper (up to first 5 chunks)
    papers_payload = []
    for p in papers:
        chunks = db.query(PaperChunk).filter(PaperChunk.paper_id == p.id).order_by(PaperChunk.chunk_index.asc()).limit(6).all()
        content_sample = "\n".join([c.content for c in chunks])
        papers_payload.append({
            "id": p.id,
            "title": p.title,
            "authors": p.authors,
            "publication_year": p.publication_year,
            "abstract": p.abstract,
            "content_sample": content_sample
        })

    # Call Gemini to generate structured comparison
    comparison_result = gemini_service.compare_papers(papers_payload)

    # Normalize list values to strings
    raw_comp_data = comparison_result.get("comparison_data", [])
    normalized_data = []
    for item in raw_comp_data:
        norm_item = item.copy()
        for k, v in norm_item.items():
            if isinstance(v, list):
                norm_item[k] = ", ".join(str(val) for val in v)
            elif v is None:
                norm_item[k] = ""
        normalized_data.append(norm_item)

    # Save to database
    comp_obj = PaperComparison(
        project_id=req.project_id,
        user_id=current_user.id,
        title=req.title or "Methodology & Findings Comparison",
        paper_ids_json=json.dumps(req.paper_ids),
        comparison_data_json=json.dumps(normalized_data),
        summary=comparison_result.get("summary", "")
    )
    db.add(comp_obj)

    log = ActivityLog(
        user_id=current_user.id,
        project_id=req.project_id,
        action="compare_papers",
        details=f"Generated comparison matrix across {len(papers)} papers"
    )
    db.add(log)
    db.commit()
    db.refresh(comp_obj)

    return {
        "id": comp_obj.id,
        "project_id": comp_obj.project_id,
        "title": comp_obj.title,
        "paper_ids": json.loads(comp_obj.paper_ids_json),
        "comparison_data": json.loads(comp_obj.comparison_data_json),
        "summary": comp_obj.summary,
        "created_at": comp_obj.created_at
    }

@router.get("/history/{project_id}", response_model=List[ComparisonResponse])
def get_comparison_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    comps = db.query(PaperComparison).filter(
        PaperComparison.project_id == project_id,
        PaperComparison.user_id == current_user.id
    ).order_by(PaperComparison.created_at.desc()).all()

    results = []
    for c in comps:
        results.append({
            "id": c.id,
            "project_id": c.project_id,
            "title": c.title,
            "paper_ids": json.loads(c.paper_ids_json or "[]"),
            "comparison_data": json.loads(c.comparison_data_json or "[]"),
            "summary": c.summary,
            "created_at": c.created_at
        })
    return results

@router.get("/{comparison_id}", response_model=ComparisonResponse)
def get_comparison(
    comparison_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    c = db.query(PaperComparison).filter(
        PaperComparison.id == comparison_id,
        PaperComparison.user_id == current_user.id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comparison record not found")

    return {
        "id": c.id,
        "project_id": c.project_id,
        "title": c.title,
        "paper_ids": json.loads(c.paper_ids_json or "[]"),
        "comparison_data": json.loads(c.comparison_data_json or "[]"),
        "summary": c.summary,
        "created_at": c.created_at
    }

@router.delete("/{comparison_id}")
def delete_comparison(
    comparison_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    c = db.query(PaperComparison).filter(
        PaperComparison.id == comparison_id,
        PaperComparison.user_id == current_user.id
    ).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comparison record not found")

    db.delete(c)
    db.commit()
    return {"message": "Comparison deleted"}
