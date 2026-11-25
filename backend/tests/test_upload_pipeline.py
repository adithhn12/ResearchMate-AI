import io
import pymupdf as fitz
from fastapi.testclient import TestClient
from app.main import app
from app.services import vector_store as vs_module
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


def test_singleton_embedding_session_reused():
    """Verify ONNX InferenceSession and Tokenizer are initialized only once across calls."""
    ef = vector_store.embedding_fn
    e1 = ef(["Transformer self-attention mechanism for sequence modeling."])
    sess_id_1 = id(vs_module._ONNX_SESSION)
    tok_id_1 = id(vs_module._TOKENIZER)

    e2 = ef(["Retrieval augmented generation improves factual grounding."])
    sess_id_2 = id(vs_module._ONNX_SESSION)
    tok_id_2 = id(vs_module._TOKENIZER)

    assert len(e1) == 1 and len(e1[0]) == 384
    assert len(e2) == 1 and len(e2[0]) == 384
    assert sess_id_1 == sess_id_2
    assert tok_id_1 == tok_id_2


def test_multi_pdf_upload_rag_and_citations():
    """Verify multi-PDF upload, chunking, ChromaDB indexing, RAG diversity, and cleanup."""
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

        paper_ids = [p["id"] for p in papers]

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


def test_upload_error_handling_meaningful_messages():
    """Verify invalid/corrupt/empty uploads return clear, specific HTTP errors."""
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
    finally:
        client.delete(f"/api/v1/projects/{project_id}", headers=headers)
