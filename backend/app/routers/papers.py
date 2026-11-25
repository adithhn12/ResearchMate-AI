import gc
import logging
import os
import shutil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models import User, Project, Paper, PaperChunk, ActivityLog
from app.schemas import PaperResponse, PaperDetailResponse
from app.auth import get_current_user
from app.services.pdf_service import PDFService
from app.services.vector_store import vector_store
from app.services.gemini_service import gemini_service

logger = logging.getLogger("researchmate.papers")

router = APIRouter(prefix="/papers", tags=["Research Papers"])


@router.post("/upload", response_model=List[PaperResponse])
def upload_papers(
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify project belongs to user
    project = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    pdf_files = [f for f in files if f.filename and f.filename.lower().endswith(".pdf")]
    if not pdf_files:
        raise HTTPException(
            status_code=400,
            detail="Only PDF files (.pdf) are supported. Please select one or more valid PDF documents.",
        )

    saved_papers: List[Paper] = []

    for file in pdf_files:
        base_name = os.path.basename(file.filename)
        safe_filename = f"proj_{project_id}_{base_name}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            try:
                file.file.close()
            except Exception:
                pass

        file_size = os.path.getsize(file_path)

        # Initial paper record
        paper = Paper(
            project_id=project_id,
            title=os.path.splitext(base_name)[0],
            file_name=base_name,
            file_path=file_path,
            file_size=file_size,
            status="processing",
        )
        db.add(paper)
        db.commit()
        db.refresh(paper)

        pages = None
        chunks = None
        chunk_objs = None

        try:
            if file_size == 0:
                raise ValueError(f"Uploaded file '{base_name}' is empty (0 bytes).")

            with open(file_path, "rb") as pdf_check:
                header = pdf_check.read(5)
            if header != b"%PDF-":
                raise ValueError(f"File '{base_name}' does not have a valid PDF header.")

            # 1. Single-pass PDF text, page count & basic metadata extraction
            pages, total_pages, basic_meta = PDFService.extract_all(file_path, base_name)
            paper.page_count = total_pages

            # 2. Refine metadata with Gemini (falls back cleanly to basic_meta)
            first_pages_text = "\n".join([p["text"] for p in pages[:2]])
            refined_meta = gemini_service.extract_paper_metadata(first_pages_text, basic_meta)

            paper.title = refined_meta.get("title") or basic_meta["title"]
            paper.authors = refined_meta.get("authors") or basic_meta["authors"]
            paper.abstract = refined_meta.get("abstract") or basic_meta["abstract"]
            paper.publication_year = refined_meta.get("publication_year") or basic_meta["publication_year"]
            paper.keywords = refined_meta.get("keywords") or basic_meta["keywords"]

            # 3. Token-aligned chunking (180 words fits within all-MiniLM-L6-v2's 256-token limit)
            chunks = PDFService.chunk_document(pages, chunk_size=180, overlap=35)
            if not chunks:
                raise ValueError(f"No indexable text chunks could be extracted from '{base_name}'.")

            # 4. Save chunks to SQLite
            chunk_objs = [
                PaperChunk(
                    paper_id=paper.id,
                    chunk_index=ch["chunk_index"],
                    page_number=ch["page_number"],
                    content=ch["content"],
                    token_count=ch.get("token_count", 0),
                )
                for ch in chunks
            ]
            db.bulk_save_objects(chunk_objs)

            # 5. Index into ChromaDB in small memory-safe batches
            vector_store.add_paper_chunks(
                project_id=project_id,
                paper_id=paper.id,
                paper_title=paper.title,
                chunks=chunks,
            )

            paper.status = "indexed"
            db.commit()
            db.refresh(paper)

            # Log activity
            log = ActivityLog(
                user_id=current_user.id,
                project_id=project_id,
                action="upload_paper",
                details=f"Uploaded and indexed paper '{paper.title}'",
            )
            db.add(log)
            db.commit()

        except Exception as e:
            logger.exception(f"Error processing paper '{base_name}': {e}")
            db.rollback()
            paper.status = "failed"
            paper.error_message = str(e)[:1000]
            db.commit()
            db.refresh(paper)
        finally:
            del pages, chunks, chunk_objs
            gc.collect()

        saved_papers.append(paper)

    # If every uploaded paper failed, return a meaningful 422 error with the root cause
    if saved_papers and all(p.status == "failed" for p in saved_papers):
        error_details = "; ".join(
            f"{p.file_name}: {p.error_message or 'Unknown processing error'}"
            for p in saved_papers
        )
        raise HTTPException(
            status_code=422,
            detail=f"Failed to process uploaded PDF(s): {error_details}",
        )

    return saved_papers


@router.get("/project/{project_id}", response_model=List[PaperResponse])
def get_project_papers(
    project_id: int,
    query: Optional[str] = Query(None, description="Search by title, authors, or abstract"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    status: Optional[str] = Query(None, description="Filter by status: indexed, processing, failed"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    proj = db.query(Project).filter(Project.id == project_id, Project.user_id == current_user.id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    q = db.query(Paper).filter(Paper.project_id == project_id)

    if query:
        search_filter = f"%{query}%"
        q = q.filter(
            (Paper.title.ilike(search_filter))
            | (Paper.authors.ilike(search_filter))
            | (Paper.abstract.ilike(search_filter))
            | (Paper.keywords.ilike(search_filter))
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
        details=f"Deleted paper '{paper_title}'",
    )
    db.add(log)
    db.commit()

    return {"message": "Paper deleted successfully"}
