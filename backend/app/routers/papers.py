import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, Project, Paper, PaperChunk, ActivityLog
from app.schemas import PaperResponse, PaperDetailResponse
from app.auth import get_current_user
from app.services.pdf_service import PDFService
from app.services.vector_store import vector_store
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/papers", tags=["Research Papers"])

@router.post("/upload", response_model=List[PaperResponse])
async def upload_papers(
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    saved_papers = []

    for file in files:
        if not file.filename.lower().endswith(".pdf"):
            continue

        # Save to disk
        safe_filename = f"proj_{project_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(file_path)

        # Initial paper record
        paper = Paper(
            project_id=project_id,
            title=os.path.splitext(file.filename)[0],
            file_name=file.filename,
            file_path=file_path,
            file_size=file_size,
            status="processing"
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)

        try:
            # 1. Extract text and page count with PyMuPDF
            pages, total_pages = PDFService.extract_text_and_pages(file_path)
            paper.page_count = total_pages

            # 2. Extract metadata
            basic_meta = PDFService.extract_basic_metadata(file_path, file.filename)
            first_pages_text = "\n".join([p["text"] for p in pages[:2]])
            refined_meta = gemini_service.extract_paper_metadata(first_pages_text, basic_meta)

            paper.title = refined_meta.get("title") or basic_meta["title"]
            paper.authors = refined_meta.get("authors") or basic_meta["authors"]
            paper.abstract = refined_meta.get("abstract") or basic_meta["abstract"]
            paper.publication_year = refined_meta.get("publication_year") or basic_meta["publication_year"]
            paper.keywords = refined_meta.get("keywords") or basic_meta["keywords"]

            # 3. Chunking
            chunks = PDFService.chunk_document(pages, chunk_size=700, overlap=120)

            # 4. Save chunks to SQLite
            chunk_objs = []
            for ch in chunks:
                chunk_obj = PaperChunk(
                    paper_id=paper.id,
                    chunk_index=ch["chunk_index"],
                    page_number=ch["page_number"],
                    content=ch["content"],
                    token_count=ch.get("token_count", 0)
                )
                chunk_objs.append(chunk_obj)
            db.bulk_save_objects(chunk_objs)

            # 5. Index into ChromaDB
            vector_store.add_paper_chunks(
                project_id=project_id,
                paper_id=paper.id,
                paper_title=paper.title,
                chunks=chunks
            )

            paper.status = "indexed"
            db.commit()
            db.refresh(paper)

            # Log activity
            log = ActivityLog(
                user_id=current_user.id,
                project_id=project_id,
                action="upload_paper",
                details=f"Uploaded and indexed paper '{paper.title}'"
            )
            db.add(log)
            db.commit()

        except Exception as e:
            paper.status = "failed"
            paper.error_message = str(e)
            db.commit()
            print(f"Error processing paper {file.filename}: {e}")

        saved_papers.append(paper)

    return saved_papers

@router.get("/project/{project_id}", response_model=List[PaperResponse])
def get_project_papers(
    project_id: int,
    query: Optional[str] = Query(None, description="Search by title, authors, or abstract"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    status: Optional[str] = Query(None, description="Filter by status: indexed, processing, failed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    q = db.query(Paper).filter(Paper.project_id == project_id)

    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            (Paper.title.ilike(search_filter)) |
            (Paper.authors.ilike(search_filter)) |
            (Paper.abstract.ilike(search_filter)) |
            (Paper.keywords.ilike(search_filter))
        )
    if year:
        q = q.filter(Paper.publication_year == year)
    if status:
        q = q.filter(Paper.status == status)

    return q.order_by(Paper.created_at.desc()).all()

@router.get("/{paper_id}", response_model=PaperDetailResponse)
def get_paper(paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = db.query(Paper).join(Project).filter(Paper.id == paper_id, Project.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    chunks_count = db.query(PaperChunk).filter(PaperChunk.paper_id == paper.id).count()
    res = PaperDetailResponse.from_orm(paper)
    res.chunks_count = chunks_count
    return res

@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    paper = db.query(Paper).join(Project).filter(Paper.id == paper_id, Project.user_id == current_user.id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    project_id = paper.project_id
    paper_title = paper.title

    # Remove from ChromaDB
    vector_store.delete_paper_chunks(project_id, paper_id)

    # Remove file from disk
    if os.path.exists(paper.file_path):
        try:
            os.remove(paper.file_path)
        except Exception:
            pass

    db.delete(paper)

    log = ActivityLog(
        user_id=current_user.id,
        project_id=project_id,
        action="delete_paper",
        details=f"Deleted paper '{paper_title}'"
    )
    db.add(log)
    db.commit()

    return {"message": "Paper deleted successfully"}
