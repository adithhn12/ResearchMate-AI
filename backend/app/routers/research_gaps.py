import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Paper, PaperChunk, ResearchGapAnalysis, ActivityLog
from app.schemas import GapAnalysisRequest, GapAnalysisResponse, GapFinding
from app.auth import get_current_user
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/gaps", tags=["Research Gap Analyzer"])

@router.post("/analyze", response_model=GapAnalysisResponse)
def analyze_gaps(
    req: GapAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not req.paper_ids:
        raise HTTPException(status_code=400, detail="Please select at least 1 research paper to analyze")

    papers = db.query(Paper).filter(Paper.id.in_(req.paper_ids), Paper.project_id == req.project_id).all()
    if not papers:
        raise HTTPException(status_code=400, detail="No matching papers found in project")

    papers_payload = []
    for p in papers:
        chunks = db.query(PaperChunk).filter(PaperChunk.paper_id == p.id).order_by(PaperChunk.chunk_index.asc()).limit(6).all()
        content_sample = "\n".join([c.content for c in chunks])
        papers_payload.append({
            "id": p.id,
            "title": p.title,
            "abstract": p.abstract,
            "content_sample": content_sample
        })

    # Call Gemini analysis
    gap_result = gemini_service.analyze_research_gaps(papers_payload)

    # Save to database
    gap_obj = ResearchGapAnalysis(
        project_id=req.project_id,
        user_id=current_user.id,
        title=req.title or "Research Gap Analysis",
        paper_ids_json=json.dumps(req.paper_ids),
        analysis_json=json.dumps(gap_result)
    )
    db.add(gap_obj)

    log = ActivityLog(
        user_id=current_user.id,
        project_id=req.project_id,
        action="analyze_gaps",
        details=f"Analyzed research gaps across {len(papers)} papers"
    )
    db.add(log)
    db.commit()
    db.refresh(gap_obj)

    return {
        "id": gap_obj.id,
        "project_id": gap_obj.project_id,
        "title": gap_obj.title,
        "paper_ids": json.loads(gap_obj.paper_ids_json),
        "recurring_challenges": gap_result.get("recurring_challenges", []),
        "gaps": gap_result.get("gaps", []),
        "created_at": gap_obj.created_at
    }

@router.get("/history/{project_id}", response_model=List[GapAnalysisResponse])
def get_gap_history(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    analyses = db.query(ResearchGapAnalysis).filter(
        ResearchGapAnalysis.project_id == project_id,
        ResearchGapAnalysis.user_id == current_user.id
    ).order_by(ResearchGapAnalysis.created_at.desc()).all()

    results = []
    for a in analyses:
        parsed = json.loads(a.analysis_json or "{}")
        results.append({
            "id": a.id,
            "project_id": a.project_id,
            "title": a.title,
            "paper_ids": json.loads(a.paper_ids_json or "[]"),
            "recurring_challenges": parsed.get("recurring_challenges", []),
            "gaps": parsed.get("gaps", []),
            "created_at": a.created_at
        })
    return results

@router.get("/{gap_id}", response_model=GapAnalysisResponse)
def get_gap_report(
    gap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    a = db.query(ResearchGapAnalysis).filter(
        ResearchGapAnalysis.id == gap_id,
        ResearchGapAnalysis.user_id == current_user.id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Gap analysis report not found")

    parsed = json.loads(a.analysis_json or "{}")
    return {
        "id": a.id,
        "project_id": a.project_id,
        "title": a.title,
        "paper_ids": json.loads(a.paper_ids_json or "[]"),
        "recurring_challenges": parsed.get("recurring_challenges", []),
        "gaps": parsed.get("gaps", []),
        "created_at": a.created_at
    }

@router.delete("/{gap_id}")
def delete_gap_report(
    gap_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    a = db.query(ResearchGapAnalysis).filter(
        ResearchGapAnalysis.id == gap_id,
        ResearchGapAnalysis.user_id == current_user.id
    ).first()
    if not a:
        raise HTTPException(status_code=404, detail="Gap analysis report not found")

    db.delete(a)
    db.commit()
    return {"message": "Gap report deleted"}
