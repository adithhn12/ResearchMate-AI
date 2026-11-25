import pytest
from app.database import SessionLocal
from app.models import User, Project, Paper, PaperChunk
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store


def test_vector_store_indexing_retrieval_and_project_isolation():
    """
    Verify external gemini-embedding-001 indexing, vector similarity retrieval,
    embedding metadata storage, and strict project-level isolation.
    """
    db = SessionLocal()
    try:
        user = User(email="vec_test@example.com", hashed_password="x", full_name="Vec Tester")
        db.add(user)
        db.commit()
        db.refresh(user)

        proj_a = Project(user_id=user.id, name="Project A", description="Isolation test A")
        proj_b = Project(user_id=user.id, name="Project B", description="Isolation test B")
        db.add_all([proj_a, proj_b])
        db.commit()
        db.refresh(proj_a)
        db.refresh(proj_b)

        paper_a = Paper(
            project_id=proj_a.id,
            title="Transformers and Dense Retrieval in Science",
            file_name="a.pdf",
            file_path="a.pdf",
            status="indexed",
        )
        paper_b = Paper(
            project_id=proj_b.id,
            title="Quantum Computing Error Correction",
            file_name="b.pdf",
            file_path="b.pdf",
            status="indexed",
        )
        db.add_all([paper_a, paper_b])
        db.commit()
        db.refresh(paper_a)
        db.refresh(paper_b)

        chunks_a = [
            {
                "chunk_index": 0,
                "page_number": 1,
                "content": "Dense retrievers utilize bi-encoder architectures to map queries and passages to dense vector spaces.",
            },
            {
                "chunk_index": 1,
                "page_number": 2,
                "content": "Evaluation metrics such as MRR@10 and Recall@5 show significant gains over BM25 lexical search.",
            },
            {
                "chunk_index": 2,
                "page_number": 3,
                "content": "A significant limitation noted by the authors is out-of-domain vocabulary mismatch and latency overhead.",
            },
        ]
        chunks_b = [
            {
                "chunk_index": 0,
                "page_number": 1,
                "content": "Surface codes protect logical qubits using topological stabilizer measurements.",
            }
        ]

        vector_store.add_paper_chunks(proj_a.id, paper_a.id, paper_a.title, chunks_a, db=db)
        vector_store.add_paper_chunks(proj_b.id, paper_b.id, paper_b.title, chunks_b, db=db)
        db.commit()

        # Verify embedding metadata persisted
        stored = db.query(PaperChunk).filter(PaperChunk.paper_id == paper_a.id).all()
        assert len(stored) == 3
        for row in stored:
            assert row.project_id == proj_a.id
            assert row.embedding_model == embedding_service.model_name
            assert row.embedding_dimensions == embedding_service.dimensions

        # Query Project A -> must return only Project A chunks
        results_a = vector_store.query_chunks(
            project_id=proj_a.id,
            query="What are the limitations and latency issues?",
            n_results=2,
            db=db,
        )
        assert len(results_a) > 0
        assert all(r["paper_id"] == paper_a.id for r in results_a)
        assert results_a[0]["paper_title"] == paper_a.title
        assert results_a[0]["page_number"] in [1, 2, 3]

        # Query Project B -> must not leak Project A chunks
        results_b = vector_store.query_chunks(
            project_id=proj_b.id,
            query="latency overhead and bi-encoder architectures",
            n_results=5,
            db=db,
        )
        assert all(r["paper_id"] == paper_b.id for r in results_b)

        vector_store.delete_project_collection(proj_a.id, db=db)
        vector_store.delete_project_collection(proj_b.id, db=db)
        db.delete(proj_a)
        db.delete(proj_b)
        db.delete(user)
        db.commit()
    finally:
        db.close()
