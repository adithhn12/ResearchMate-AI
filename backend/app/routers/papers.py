import gc
import logging
import os
import shutil
import tempfile
import threading
import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, Form, Query, status
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal, get_db
from app.models import User, Project, Paper, PaperChunk, ActivityLog
from app.schemas import PaperResponse, PaperDetailResponse
from app.auth import get_current_user
from app.services.pdf_service import PDFService
from app.services.vector_store import vector_store
from app.services.gemini_service import gemini_service
from app.services.storage_service import storage_service

logger = logging.getLogger("researchmate.papers")

router = APIRouter(prefix="/papers", tags=["Research Papers"])

# Limit concurrent background PDF ingestion to 1 at a time to protect 512 MB RAM on Render Free Tier
_INGEST_SEMAPHORE = threading.BoundedSemaphore(1)


def _process_papers_in_background(jobs: List[Dict[str, Any]], project_id: int, user_id: int) -> None:
    """
    Sequentially process uploaded PDFs in the background:
    extract text/metadata -> chunk -> external Gemini embeddings -> pgvector -> Supabase Storage.
    """
    with _INGEST_SEMAPHORE:
        db = SessionLocal()
        try:
            for job in jobs:
                paper_id = job["paper_id"]
                temp_path = job["temp_path"]
                base_name = job["base_name"]
                object_key = job["object_key"]
                previous_remote_key = job.get("previous_remote_key")

                paper = db.query(Paper).filter(Paper.id == paper_id).first()
                if not paper:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                    continue

                pages = None
                chunks = None
                uploaded_remote_key = None

                try:
                    paper.status = "processing"
                    paper.error_message = None
                    db.commit()

                    # 1. Single-pass PDF text, page count & basic metadata extraction (sanitized)
                    pages, total_pages, basic_meta = PDFService.extract_all(temp_path, base_name)
                    if total_pages > settings.MAX_PDF_PAGES:
                        raise ValueError(
                            f"PDF '{base_name}' has {total_pages} pages, exceeding the {settings.MAX_PDF_PAGES}-page limit."
                        )
                    paper.page_count = total_pages

                    # 2. Refine metadata with Gemini (falls back cleanly to basic_meta)
                    first_pages_text = "\n".join([p["text"] for p in pages[:2]])
                    refined_meta = gemini_service.extract_paper_metadata(first_pages_text, basic_meta)

                    paper.title = PDFService.sanitize_text(refined_meta.get("title") or basic_meta["title"])[:500]
                    paper.authors = PDFService.sanitize_text(refined_meta.get("authors") or basic_meta["authors"])[:500]
                    paper.abstract = PDFService.sanitize_text(refined_meta.get("abstract") or basic_meta["abstract"])
                    paper.publication_year = refined_meta.get("publication_year") or basic_meta["publication_year"]
                    paper.keywords = PDFService.sanitize_text(refined_meta.get("keywords") or basic_meta["keywords"])[:500]

                    # 3. Bounded chunking (180 words, 35 overlap)
                    chunks = PDFService.chunk_document(pages, chunk_size=180, overlap=35)
                    del pages
                    pages = None
                    if not chunks:
                        raise ValueError(f"No indexable text chunks could be extracted from '{base_name}'.")

                    # 4. Generate external Gemini embeddings in bounded batches and stage chunks in pgvector
                    vector_store.add_paper_chunks(
                        project_id=project_id,
                        paper_id=paper.id,
                        paper_title=paper.title,
                        chunks=chunks,
                        db=db,
                    )

                    # 5. Upload PDF to Supabase Storage only after extraction/embedding succeeded
                    if storage_service.is_configured():
                        uploaded_remote_key = storage_service.upload_pdf(temp_path, object_key)
                        paper.storage_path = uploaded_remote_key
                        paper.file_path = uploaded_remote_key

                    paper.status = "indexed"
                    paper.error_message = None
                    db.commit()

                    if previous_remote_key and previous_remote_key != uploaded_remote_key:
                        storage_service.delete_pdf(previous_remote_key)

                    log = ActivityLog(
                        user_id=user_id,
                        project_id=project_id,
                        action="upload_paper",
                        details=f"Uploaded and indexed paper '{paper.title}'",
                    )
                    db.add(log)
                    db.commit()

                except Exception as e:
                    logger.exception(f"Background ingestion failed for paper '{base_name}' (id={paper_id}): {e}")
                    db.rollback()
                    if uploaded_remote_key:
                        storage_service.delete_pdf(uploaded_remote_key)
                    paper = db.query(Paper).filter(Paper.id == paper_id).first()
                    if paper:
                        paper.storage_path = previous_remote_key
                        paper.status = "failed"
                        paper.error_message = PDFService.sanitize_text(str(e))[:1000]
                        db.commit()
                finally:
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except Exception:
                            pass
                    del pages, chunks
                    gc.collect()
        finally:
            db.close()


@router.post("/upload", response_model=List[PaperResponse], status_code=status.HTTP_202_ACCEPTED)
def upload_papers(
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    if len(pdf_files) > settings.MAX_FILES_PER_UPLOAD:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_FILES_PER_UPLOAD} PDF files can be uploaded per request.",
        )

    max_bytes = settings.MAX_UPLOAD_FILE_MB * 1024 * 1024
    queued_papers: List[Paper] = []
    bg_jobs: List[Dict[str, Any]] = []

    try:
        for file in pdf_files:
            base_name = os.path.basename(file.filename)
            temp_path = None

            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf", dir=settings.UPLOAD_DIR
                ) as tmp:
                    temp_path = tmp.name
                    shutil.copyfileobj(file.file, tmp, length=65536)
            finally:
                try:
                    file.file.close()
                except Exception:
                    pass

            file_size = os.path.getsize(temp_path) if temp_path and os.path.exists(temp_path) else 0

            # Fast upfront validation before queuing background work
            if file_size == 0:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                raise HTTPException(
                    status_code=422,
                    detail=f"Uploaded file '{base_name}' is empty (0 bytes).",
                )

            if file_size > max_bytes:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File '{base_name}' exceeds the {settings.MAX_UPLOAD_FILE_MB} MB upload limit.",
                )

            with open(temp_path, "rb") as pdf_check:
                header = pdf_check.read(5)
            if header != b"%PDF-":
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                raise HTTPException(
                    status_code=422,
                    detail=f"File '{base_name}' does not have a valid PDF header.",
                )

            existing = (
                db.query(Paper)
                .filter(Paper.project_id == project_id, Paper.file_name == base_name)
                .first()
            )

            # Prevent duplicate concurrent ingestion if already pending/processing
            if existing and existing.status in ("pending", "processing"):
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                queued_papers.append(existing)
                continue

            object_key = f"project_{project_id}/{uuid.uuid4().hex}_{base_name}"
            previous_remote_key = None

            if existing:
                previous_remote_key = existing.storage_path
                existing.file_path = object_key
                existing.storage_path = None
                existing.file_size = file_size
                existing.status = "pending"
                existing.error_message = None
                db.query(PaperChunk).filter(PaperChunk.paper_id == existing.id).delete(
                    synchronize_session=False
                )
                paper = existing
            else:
                paper = Paper(
                    project_id=project_id,
                    title=os.path.splitext(base_name)[0],
                    file_name=base_name,
                    file_path=object_key,
                    storage_path=None,
                    file_size=file_size,
                    status="pending",
                )
                db.add(paper)

            db.commit()
            db.refresh(paper)

            queued_papers.append(paper)
            bg_jobs.append(
                {
                    "paper_id": paper.id,
                    "temp_path": temp_path,
                    "base_name": base_name,
                    "object_key": object_key,
                    "previous_remote_key": previous_remote_key,
                }
            )
    except Exception:
        # Clean up any temp files already created in this failed request
        for job in bg_jobs:
            tp = job.get("temp_path")
            if tp and os.path.exists(tp):
                try:
                    os.remove(tp)
                except Exception:
                    pass
        raise

    if bg_jobs:
        background_tasks.add_task(_process_papers_in_background, bg_jobs, project_id, current_user.id)

    return queued_papers


@router.get("/status", response_model=List[PaperResponse])
def get_ingestion_status(
    paper_ids: List[int] = Query(..., description="Paper IDs to poll for ingestion status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Poll ingestion status (pending, processing, indexed, failed) for uploaded papers."""
    if not paper_ids:
        return []
    papers = (
        db.query(Paper)
        .join(Project)
        .filter(Paper.id.in_(paper_ids), Project.user_id == current_user.id)
        .all()
    )
    return papers


@router.get("/project/{project_id}", response_model=List[PaperResponse])
def get_project_papers(
    project_id: int,
    query: Optional[str] = Query(None, description="Search by title, authors, or abstract"),
    year: Optional[int] = Query(None, description="Filter by publication year"),
    status: Optional[str] = Query(None, description="Filter by status: pending, processing, indexed, failed"),
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
    remote_key = paper.storage_path or paper.file_path

    # Remove vector chunks
    vector_store.delete_paper_chunks(project_id, paper_id, db=db)

    # Remove from Supabase Storage if configured
    if remote_key:
        storage_service.delete_pdf(remote_key)

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
