import os
import pytest
import pymupdf as fitz
from app.services.pdf_service import PDFService

@pytest.fixture
def sample_pdf(tmp_path):
    """Creates a temporary sample academic PDF for testing."""
    pdf_path = str(tmp_path / "test_research_paper.pdf")
    doc = fitz.open()

    # Page 1: Title, Authors, Abstract, Introduction
    p1 = doc.new_page()
    text_p1 = """
Attention Mechanisms and Retrieval Augmented Generation in Academic Research
Dr. Elena Rostova, Prof. Marcus Chen
Department of Computer Science, Stanford University

Abstract
This paper presents a novel framework for multi-document retrieval augmented generation (RAG).
We evaluate transformer-based dense embeddings and cross-attention reranking mechanisms on academic benchmark datasets.
Our findings demonstrate a 14.2% improvement in factual citation precision compared to standard baseline retrievers.

Keywords: Retrieval Augmented Generation, Transformers, Embeddings, Academic Literature

1. Introduction
Modern scholarly research is characterized by exponential literature growth. Researchers frequently struggle to synthesize findings across disparate corpora. In this work, we systematically investigate chunking trade-offs and vector similarity thresholds.
"""
    p1.insert_text((50, 72), text_p1, fontsize=11)

    # Page 2: Methodology, Limitations, Conclusion
    p2 = doc.new_page()
    text_p2 = """
2. Methodology & Experimental Setup
We benchmarked our system using ChromaDB vector store coupled with all-MiniLM-L6-v2 sentence embeddings.
Chunks of 500 characters with 100 character overlaps were extracted and indexed.

3. Limitations & Constraints
A prominent limitation of our approach is the quadratic memory scaling with long sequence contexts.
Additionally, our model was evaluated primarily on English language computer science papers, leaving multi-lingual generalization unexplored.

4. Conclusion & Future Work
We established that structured retrieval pipelines significantly reduce factual hallucination.
Future research should investigate parameter-efficient distillation and cross-lingual multi-modal embeddings.
"""
    p2.insert_text((50, 72), text_p2, fontsize=11)

    doc.save(pdf_path)
    doc.close()
    return pdf_path

def test_extract_text_and_pages(sample_pdf):
    pages, total_pages = PDFService.extract_text_and_pages(sample_pdf)
    assert total_pages == 2
    assert len(pages) == 2
    assert pages[0]["page_number"] == 1
    assert "Attention Mechanisms" in pages[0]["text"]
    assert pages[1]["page_number"] == 2
    assert "Limitations & Constraints" in pages[1]["text"]

def test_extract_basic_metadata(sample_pdf):
    meta = PDFService.extract_basic_metadata(sample_pdf, "test_research_paper.pdf")
    assert meta["title"] is not None
    assert len(meta["title"]) > 0
    assert meta["abstract"] is not None
    assert "multi-document retrieval" in meta["abstract"].lower()
    assert meta["keywords"] is not None

def test_chunking_with_page_metadata(sample_pdf):
    pages, total_pages = PDFService.extract_text_and_pages(sample_pdf)
    chunks = PDFService.chunk_document(pages, chunk_size=100, overlap=20)
    assert len(chunks) > 0
    for chunk in chunks:
        assert "chunk_index" in chunk
        assert "page_number" in chunk
        assert chunk["page_number"] in [1, 2]
        assert len(chunk["content"]) > 0
