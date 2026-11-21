import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Project, Paper, PaperChunk, LiteratureReview, ActivityLog
from app.schemas import (
    LiteratureReviewGenerateRequest,
    LiteratureReviewUpdateRequest,
    LiteratureReviewResponse
)
from app.auth import get_current_user
from app.services.gemini_service import gemini_service
from app.services.export_service import export_service

router = APIRouter(prefix="/reviews", tags=["Literature Review Generator"])

@router.post("/generate", response_model=LiteratureReviewResponse)
def generate_review(
    req: LiteratureReviewGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == req.project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not req.paper_ids:
        raise HTTPException(status_code=400, detail="Please select at least 1 research paper to generate a literature review")

    papers = db.query(Paper).filter(Paper.id.in_(req.paper_ids), Paper.project_id == req.project_id).all()
    if not papers:
        raise HTTPException(status_code=400, detail="No matching papers found")

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

    # Call Gemini review generation
    title = req.title or f"Literature Review: {papers[0].title[:50]}"
    gen_result = gemini_service.generate_literature_review(
        papers=papers_payload,
        title=title,
        research_focus=req.research_focus
    )

    def _to_str(val):
        if val is None:
            return ""
        if isinstance(val, list):
            return "\n\n".join([str(item) for item in val])
        return str(val)

    review_obj = LiteratureReview(
        project_id=req.project_id,
        user_id=current_user.id,
        title=gen_result.get("title", title),
        paper_ids_json=json.dumps(req.paper_ids),
        introduction=_to_str(gen_result.get("introduction")),
        background_related_work=_to_str(gen_result.get("background_related_work")),
        thematic_analysis=_to_str(gen_result.get("thematic_analysis")),
        comparison_existing_approaches=_to_str(gen_result.get("comparison_existing_approaches")),
        research_limitations=_to_str(gen_result.get("research_limitations")),
        research_gaps=_to_str(gen_result.get("research_gaps")),
        conclusion=_to_str(gen_result.get("conclusion")),
        references=_to_str(gen_result.get("references"))
    )
    db.add(review_obj)

    log = ActivityLog(
        user_id=current_user.id,
        project_id=req.project_id,
        action="generate_literature_review",
        details=f"Generated literature review '{review_obj.title}'"
    )
    db.add(log)
    db.commit()
    db.refresh(review_obj)

    return {
        "id": review_obj.id,
        "project_id": review_obj.project_id,
        "title": review_obj.title,
        "paper_ids": json.loads(review_obj.paper_ids_json),
        "introduction": review_obj.introduction,
        "background_related_work": review_obj.background_related_work,
        "thematic_analysis": review_obj.thematic_analysis,
        "comparison_existing_approaches": review_obj.comparison_existing_approaches,
        "research_limitations": review_obj.research_limitations,
        "research_gaps": review_obj.research_gaps,
        "conclusion": review_obj.conclusion,
        "references": review_obj.references,
        "created_at": review_obj.created_at,
        "updated_at": review_obj.updated_at
    }

@router.get("/project/{project_id}", response_model=List[LiteratureReviewResponse])
def get_project_reviews(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    reviews = db.query(LiteratureReview).filter(
        LiteratureReview.project_id == project_id,
        LiteratureReview.user_id == current_user.id
    ).order_by(LiteratureReview.updated_at.desc()).all()

    results = []
    for r in reviews:
        results.append({
            "id": r.id,
            "project_id": r.project_id,
            "title": r.title,
            "paper_ids": json.loads(r.paper_ids_json or "[]"),
            "introduction": r.introduction,
            "background_related_work": r.background_related_work,
            "thematic_analysis": r.thematic_analysis,
            "comparison_existing_approaches": r.comparison_existing_approaches,
            "research_limitations": r.research_limitations,
            "research_gaps": r.research_gaps,
            "conclusion": r.conclusion,
            "references": r.references,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        })
    return results

@router.get("/{review_id}", response_model=LiteratureReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(LiteratureReview).filter(
        LiteratureReview.id == review_id,
        LiteratureReview.user_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Literature review not found")

    return {
        "id": r.id,
        "project_id": r.project_id,
        "title": r.title,
        "paper_ids": json.loads(r.paper_ids_json or "[]"),
        "introduction": r.introduction,
        "background_related_work": r.background_related_work,
        "thematic_analysis": r.thematic_analysis,
        "comparison_existing_approaches": r.comparison_existing_approaches,
        "research_limitations": r.research_limitations,
        "research_gaps": r.research_gaps,
        "conclusion": r.conclusion,
        "references": r.references,
        "created_at": r.created_at,
        "updated_at": r.updated_at
    }

@router.put("/{review_id}", response_model=LiteratureReviewResponse)
def update_review(
    review_id: int,
    req: LiteratureReviewUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(LiteratureReview).filter(
        LiteratureReview.id == review_id,
        LiteratureReview.user_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Literature review not found")

    if req.title is not None:
        r.title = req.title
    if req.introduction is not None:
        r.introduction = req.introduction
    if req.background_related_work is not None:
        r.background_related_work = req.background_related_work
    if req.thematic_analysis is not None:
        r.thematic_analysis = req.thematic_analysis
    if req.comparison_existing_approaches is not None:
        r.comparison_existing_approaches = req.comparison_existing_approaches
    if req.research_limitations is not None:
        r.research_limitations = req.research_limitations
    if req.research_gaps is not None:
        r.research_gaps = req.research_gaps
    if req.conclusion is not None:
        r.conclusion = req.conclusion
    if req.references is not None:
        r.references = req.references

    db.commit()
    db.refresh(r)

    return {
        "id": r.id,
        "project_id": r.project_id,
        "title": r.title,
        "paper_ids": json.loads(r.paper_ids_json or "[]"),
        "introduction": r.introduction,
        "background_related_work": r.background_related_work,
        "thematic_analysis": r.thematic_analysis,
        "comparison_existing_approaches": r.comparison_existing_approaches,
        "research_limitations": r.research_limitations,
        "research_gaps": r.research_gaps,
        "conclusion": r.conclusion,
        "references": r.references,
        "created_at": r.created_at,
        "updated_at": r.updated_at
    }

@router.get("/{review_id}/export/docx")
def export_docx(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(LiteratureReview).filter(
        LiteratureReview.id == review_id,
        LiteratureReview.user_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Literature review not found")

    review_dict = {
        "title": r.title,
        "introduction": r.introduction,
        "background_related_work": r.background_related_work,
        "thematic_analysis": r.thematic_analysis,
        "comparison_existing_approaches": r.comparison_existing_approaches,
        "research_limitations": r.research_limitations,
        "research_gaps": r.research_gaps,
        "conclusion": r.conclusion,
        "references": r.references
    }
    docx_buffer = export_service.generate_docx(review_dict)
    filename = f"literature_review_{review_id}.docx"
    return StreamingResponse(
        docx_buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/{review_id}/export/pdf")
def export_pdf(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(LiteratureReview).filter(
        LiteratureReview.id == review_id,
        LiteratureReview.user_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Literature review not found")

    review_dict = {
        "title": r.title,
        "introduction": r.introduction,
        "background_related_work": r.background_related_work,
        "thematic_analysis": r.thematic_analysis,
        "comparison_existing_approaches": r.comparison_existing_approaches,
        "research_limitations": r.research_limitations,
        "research_gaps": r.research_gaps,
        "conclusion": r.conclusion,
        "references": r.references
    }
    pdf_buffer = export_service.generate_pdf(review_dict)
    filename = f"literature_review_{review_id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    r = db.query(LiteratureReview).filter(
        LiteratureReview.id == review_id,
        LiteratureReview.user_id == current_user.id
    ).first()
    if not r:
        raise HTTPException(status_code=404, detail="Literature review not found")

    db.delete(r)
    db.commit()
    return {"message": "Literature review deleted"}
