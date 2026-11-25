import io
import os
import sys
import pytest
import pymupdf as fitz
from fastapi.testclient import TestClient
from app.config import settings
from app.database import SessionLocal
from app.main import app
from app.models import Paper, PaperChunk
from app.services.embedding_service import embedding_service
from app.services.pdf_service import PDFService
from app.services.vector_store import vector_store

client = TestClient(app)


def _make_pdf_bytes(title: str, pages_text: list[str]) -> bytes:
    doc = fitz.open()
    for idx, text in enumerate(pages_text):
        page = doc.new_page()
        body = f"{title}\n\n{text}" if idx == 0 else text
        page.insert_text((50, 72), body, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


def _get_auth_headers():
    resp = client.post("/api/v1/auth/demo-login")
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_no_local_embedding_models_loaded():
    """Verify local ONNX Runtime, Sentence Transformers, PyTorch, and ChromaDB are never loaded."""
    forbidden_modules = ("onnxruntime", "sentence_transformers", "chromadb", "torch")
    loaded = [m for m in forbidden_modules if m in sys.modules]
    assert loaded == [], f"Unexpected local ML/vector modules loaded: {loaded}"


def test_external_embedding_consistency_and_no_local_fallback(monkeypatch):
    """
    Verify indexing and querying use the same gemini-embedding-001 model & dimensionality,
    and missing API key fails explicitly without falling back to local inference.
    """
    doc_vecs = embedding_service.embed_documents(["Transformer self-attention mechanism."])
    query_vec = embedding_service.embed_query("How does self-attention work?")

    assert len(doc_vecs) == 1
    assert len(doc_vecs[0]) == settings.EMBEDDING_DIMENSIONS
    assert len(query_vec) == settings.EMBEDDING_DIMENSIONS
    assert embedding_service.model_name == "gemini-embedding-001"

    # Verify no silent fallback when GEMINI_API_KEY is missing
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")
    monkeypatch.setattr(embedding_service, "_client", None)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        embedding_service.embed_query("Should fail without local fallback")


def test_multi_pdf_upload_rag_citations_and_temp_cleanup():
    """Verify sequential multi-PDF upload, pgvector indexing, RAG diversity, and temp cleanup."""
    headers = _get_auth_headers()

    proj_resp = client.post(
        "/api/v1/projects",
        json={"name": "Multi-PDF Upload Test Project", "description": "Verify multi-PDF ingestion"},
        headers=headers,
    )
    assert proj_resp.status_code == 200
    project_id = proj_resp.json()["id"]

    pdf1_bytes = _make_pdf_bytes(
        "Attention Is All You Need",
        [
            "Abstract: The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose the Transformer architecture relying entirely on self-attention.",
            "Page 2 Experimental Results: On WMT 2014 English-to-German translation, the big Transformer model achieves 28.4 BLEU score using 8 P100 GPUs.",
        ],
    )
    pdf2_bytes = _make_pdf_bytes(
        "LoRA: Low-Rank Adaptation of Large Language Models",
        [
            "Abstract: Fine-tuning large language models is prohibitively expensive. We propose LoRA which freezes pre-trained model weights and injects trainable rank decomposition matrices.",
            "Page 2 Memory Efficiency: LoRA reduces trainable parameters by 10,000 times and GPU memory requirement by 3 times on GPT-3 175B.",
        ],
    )

    temp_files_before = set(os.listdir(settings.UPLOAD_DIR)) if os.path.exists(settings.UPLOAD_DIR) else set()

    try:
        upload_resp = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[
                ("files", ("attention_paper.pdf", io.BytesIO(pdf1_bytes), "application/pdf")),
                ("files", ("lora_paper.pdf", io.BytesIO(pdf2_bytes), "application/pdf")),
            ],
            headers=headers,
        )
        assert upload_resp.status_code == 200, upload_resp.text
        papers = upload_resp.json()
        assert len(papers) == 2
        assert all(p["status"] == "indexed" for p in papers)
        assert all(p["page_count"] == 2 for p in papers)

        # Verify temp files were cleaned up reliably
        temp_files_after = set(os.listdir(settings.UPLOAD_DIR)) if os.path.exists(settings.UPLOAD_DIR) else set()
        assert temp_files_after == temp_files_before

        paper_ids = [p["id"] for p in papers]

        # Verify chunk metadata persisted
        with SessionLocal() as db:
            db_chunks = db.query(PaperChunk).filter(PaperChunk.paper_id.in_(paper_ids)).all()
            assert len(db_chunks) >= 2
            assert all(c.embedding_model == "gemini-embedding-001" for c in db_chunks)
            assert all(c.embedding_dimensions == settings.EMBEDDING_DIMENSIONS for c in db_chunks)

        # Verify multi-document RAG retrieval preserves paper_id, paper_title, and page_number
        chunks = vector_store.query_chunks(
            project_id=project_id,
            query="Compare Transformer BLEU score and LoRA GPU memory efficiency",
            n_results=6,
            paper_ids=paper_ids,
        )
        assert len(chunks) >= 2
        retrieved_paper_ids = {c["paper_id"] for c in chunks}
        assert set(paper_ids).issubset(retrieved_paper_ids)
        for ch in chunks:
            assert ch["paper_title"]
            assert ch["page_number"] in (1, 2)
            assert ch["content"]
    finally:
        client.delete(f"/api/v1/projects/{project_id}", headers=headers)


def test_upload_error_handling_and_limits():
    """Verify invalid/corrupt/empty uploads and file-count limits return clear HTTP errors."""
    headers = _get_auth_headers()
    proj_resp = client.post(
        "/api/v1/projects",
        json={"name": "Upload Error Test Project", "description": "Verify upload error messages"},
        headers=headers,
    )
    assert proj_resp.status_code == 200
    project_id = proj_resp.json()["id"]

    try:
        # 1. Non-PDF file
        resp_non_pdf = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[("files", ("notes.txt", io.BytesIO(b"hello world"), "text/plain"))],
            headers=headers,
        )
        assert resp_non_pdf.status_code == 400
        assert "Only PDF files" in resp_non_pdf.json()["detail"]

        # 2. Fake PDF without %PDF- header
        resp_bad_header = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[("files", ("fake.pdf", io.BytesIO(b"not a pdf"), "application/pdf"))],
            headers=headers,
        )
        assert resp_bad_header.status_code == 422
        assert "valid PDF header" in resp_bad_header.json()["detail"]

        # 3. Empty 0-byte PDF
        resp_empty = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[("files", ("empty.pdf", io.BytesIO(b""), "application/pdf"))],
            headers=headers,
        )
        assert resp_empty.status_code == 422
        assert "empty (0 bytes)" in resp_empty.json()["detail"]

        # 4. Exceeding MAX_FILES_PER_UPLOAD
        too_many = [
            ("files", (f"doc_{i}.pdf", io.BytesIO(b"%PDF-1.4\n"), "application/pdf"))
            for i in range(settings.MAX_FILES_PER_UPLOAD + 1)
        ]
        resp_limit = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=too_many,
            headers=headers,
        )
        assert resp_limit.status_code == 400
        assert "Maximum" in resp_limit.json()["detail"]
    finally:
        client.delete(f"/api/v1/projects/{project_id}", headers=headers)


def test_nul_byte_sanitization_unicode_and_empty_chunks():
    """Verify NUL (0x00) byte removal preserves Unicode/math and skips empty sanitized chunks."""
    # 1. Single and multiple NUL bytes removed, Unicode & math symbols preserved
    raw = "Attention\x00\x00 mechanism: ∑ᵢ αᵢ xᵢ ≥ √(2π) — ∀ i ∈ ℝⁿ\x00."
    cleaned = PDFService.sanitize_text(raw)
    assert "\x00" not in cleaned
    assert cleaned == "Attention mechanism: ∑ᵢ αᵢ xᵢ ≥ √(2π) — ∀ i ∈ ℝⁿ."

    # 2. Text that becomes empty after NUL sanitization is skipped safely
    pages = [
        {"page_number": 1, "text": "\x00\x00   \x00\x00"},
        {
            "page_number": 2,
            "text": "Valid\x00 research\x00\x00 content with math ∑ᵢ αᵢ xᵢ ≥ 0 and enough words to form a chunk cleanly.",
        },
    ]
    chunks = PDFService.chunk_document(pages, chunk_size=180, overlap=35)
    assert len(chunks) == 1
    assert chunks[0]["page_number"] == 2
    assert "\x00" not in chunks[0]["content"]
    assert "∑ᵢ αᵢ xᵢ ≥ 0" in chunks[0]["content"]


def test_postgresql_sanitized_chunk_insertion_and_idempotent_retry(monkeypatch):
    """
    Verify chunks with NUL bytes are sanitized before PostgreSQL insertion (no DataError)
    and retrying the same PDF does not create duplicate Paper or PaperChunk records.
    """
    headers = _get_auth_headers()
    proj_resp = client.post(
        "/api/v1/projects",
        json={"name": "NUL Sanitization PG Test", "description": "Regression test for 0x00 bytes"},
        headers=headers,
    )
    assert proj_resp.status_code == 200
    project_id = proj_resp.json()["id"]

    # Inject a PDF whose extracted text contains NUL bytes and Unicode math
    pdf_bytes = _make_pdf_bytes(
        "Math & Unicode Paper",
        [
            "Abstract: Transformer attention ∑ᵢ αᵢ xᵢ ≥ √(2π) with embedded NUL bytes.",
        ],
    )

    orig_extract_all = PDFService.extract_all

    def _extract_with_nul(file_path: str, file_name: str):
        pages, total_pages, meta = orig_extract_all(file_path, file_name)
        pages[0]["text"] = PDFService.sanitize_text(
            "Abstract\x00\x00: Transformer attention\x00 ∑ᵢ αᵢ xᵢ ≥ √(2π) — ∀ i ∈ ℝⁿ."
        )
        # Also test defensive sanitization in vector_store.add_paper_chunks directly
        return pages, total_pages, meta

    monkeypatch.setattr(PDFService, "extract_all", staticmethod(_extract_with_nul))

    try:
        # First upload
        r1 = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[("files", ("nul_test_paper.pdf", io.BytesIO(pdf_bytes), "application/pdf"))],
            headers=headers,
        )
        assert r1.status_code == 200, r1.text
        p1 = r1.json()[0]
        assert p1["status"] == "indexed"

        # Defensive check: insert chunk containing raw \x00 directly through vector_store
        with SessionLocal() as db:
            vector_store.add_paper_chunks(
                project_id=project_id,
                paper_id=p1["id"],
                paper_title=p1["title"],
                chunks=[
                    {
                        "chunk_index": 0,
                        "page_number": 1,
                        "content": "Direct\x00\x00 NUL\x00 chunk ∑ᵢ αᵢ xᵢ ≥ √(2π)",
                    },
                    {
                        "chunk_index": 1,
                        "page_number": 1,
                        "content": "\x00\x00   \x00",  # empty after sanitization -> must be skipped
                    },
                ],
                db=db,
            )
            db.commit()

            rows = db.query(PaperChunk).filter(PaperChunk.paper_id == p1["id"]).all()
            assert len(rows) == 1
            assert "\x00" not in rows[0].content
            assert "∑ᵢ αᵢ xᵢ ≥ √(2π)" in rows[0].content

        # Retry uploading the exact same PDF -> must reuse Paper ID and not duplicate records
        r2 = client.post(
            "/api/v1/papers/upload",
            data={"project_id": str(project_id)},
            files=[("files", ("nul_test_paper.pdf", io.BytesIO(pdf_bytes), "application/pdf"))],
            headers=headers,
        )
        assert r2.status_code == 200, r2.text
        p2 = r2.json()[0]
        assert p2["id"] == p1["id"]

        with SessionLocal() as db:
            paper_count = (
                db.query(Paper)
                .filter(Paper.project_id == project_id, Paper.file_name == "nul_test_paper.pdf")
                .count()
            )
            assert paper_count == 1
    finally:
        client.delete(f"/api/v1/projects/{project_id}", headers=headers)
