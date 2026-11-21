import pytest
from app.services.vector_store import vector_store

def test_vector_store_indexing_and_retrieval():
    test_project_id = 9999
    paper_id = 101
    paper_title = "Transformers and Dense Retrieval in Science"
    
    chunks = [
        {
            "chunk_index": 0,
            "page_number": 1,
            "content": "Dense retrievers utilize bi-encoder architectures to map queries and passages to dense vector spaces."
        },
        {
            "chunk_index": 1,
            "page_number": 2,
            "content": "Evaluation metrics such as MRR@10 and Recall@5 show significant gains over BM25 lexical search."
        },
        {
            "chunk_index": 2,
            "page_number": 3,
            "content": "A significant limitation noted by the authors is out-of-domain vocabulary mismatch and latency overhead."
        }
    ]

    # Index chunks
    vector_store.add_paper_chunks(
        project_id=test_project_id,
        paper_id=paper_id,
        paper_title=paper_title,
        chunks=chunks
    )

    # Query
    results = vector_store.query_chunks(
        project_id=test_project_id,
        query="What are the limitations and latency issues?",
        n_results=2
    )

    assert len(results) > 0
    assert results[0]["paper_id"] == paper_id
    assert results[0]["paper_title"] == paper_title
    assert results[0]["page_number"] in [1, 2, 3]
    assert "content" in results[0]

    # Test clean up
    vector_store.delete_paper_chunks(test_project_id, paper_id)
    vector_store.delete_project_collection(test_project_id)
