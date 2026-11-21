import os
import pymupdf as fitz

def create_sample_papers():
    output_dir = "sample_papers"
    os.makedirs(output_dir, exist_ok=True)

    papers_data = [
        {
            "filename": "multi_doc_rag_synthesis.pdf",
            "title": "Multi-Document Retrieval-Augmented Generation for Scientific Knowledge Synthesis",
            "authors": "Dr. Sarah Lin, Prof. David K. Miller",
            "institution": "Department of Artificial Intelligence, MIT & Stanford University",
            "abstract": "Retrieval-Augmented Generation (RAG) has emerged as the state-of-the-art paradigm for grounding Large Language Models (LLMs) in verifiable scientific literature. However, existing single-document retrieval architectures often fail to aggregate contradictory or complementary findings dispersed across multi-paper corpora. In this paper, we propose ChronoRAG, a multi-document synthesis framework featuring hierarchical dense chunking and cross-attention passage reranking. Evaluating across 2,400 peer-reviewed biomedical and computer science papers, our method achieves an 18.4% improvement in factual citation precision (p < 0.01) and reduces hallucination frequency to 2.1%.",
            "keywords": "Retrieval-Augmented Generation, Multi-Document Synthesis, Dense Retrieval, ChromaDB, Hallucination Reduction",
            "pages": [
                """1. Introduction
Academic research is expanding at an unprecedented rate, with over 3 million peer-reviewed papers published annually. Researchers face severe cognitive overload attempting to synthesize methodological trade-offs, empirical baselines, and emerging limitations across disparate sources.
While standard LLMs possess vast general knowledge, their static parameter weights suffer from temporal cutoffs, factual inaccuracies, and catastrophic hallucination when queried regarding domain-specific scientific literature.

2. Related Work
Dense passage retrieval (DPR) models, primarily relying on bi-encoder architectures like all-MiniLM-L6-v2, map text chunks into 384-dimensional continuous vector spaces. While BM25 provides lexical precision, semantic embeddings capture conceptual synonymy and paraphrasing. Recent works by Lewis et al. demonstrated the efficacy of retrieval grounding, but cross-document aggregation remains an open research frontier.""",

                """3. Proposed Methodology
Our framework operates in three distinct phases:
1. Document Preprocessing: PDFs are parsed page-by-page using PyMuPDF, extracting bibliographic headers, abstracts, and body sections. Text is partitioned into 700-character chunks with a 120-character sliding window to maintain paragraph coherence.
2. Embedding and Vector Indexing: Chunks are projected using HuggingFace all-MiniLM-L6-v2 models and persisted in ChromaDB collections, with metadata tracking project IDs, paper identifiers, and physical page numbers.
3. Grounded Synthesis: At query time, top-k passages are retrieved via cosine similarity and submitted to Google Gemini with strict prompt constraints forbidding hallucinated citations.

4. Empirical Results & Discussion
On the SciRepEval benchmark, ChronoRAG achieved an MRR@10 of 0.842 and an F1 score of 89.2% on question answering, significantly outperforming unaugmented baseline models (F1: 67.4%).""",

                """5. Limitations and Constraints
Despite empirical strengths, several explicit limitations must be highlighted:
- Scalability to Extremely Large Corpora: Vector search latency increases linearly when corpus size exceeds 100,000 document chunks without hierarchical HNSW partitioning.
- High-Density Mathematical Formulations: PyMuPDF extraction occasionally strips LaTeX math symbols and inline equation formatting, leading to incomplete retrieval of mathematical proofs.
- Context Window Saturation: Aggregating excerpts from more than 15 documents simultaneously risks context saturation in fixed-window LLM attention heads.

6. Conclusion & Future Research Directions
We demonstrated that multi-document RAG provides verifiable, reproducible academic assistance. Future research directions should investigate multi-modal chart and table extraction, federated vector collections across institutions, and automated hypothesis generation based on identified literature gaps."""
            ]
        },
        {
            "filename": "lightweight_embeddings_evaluation.pdf",
            "title": "Empirical Evaluation of Lightweight Embedding Models on Domain-Specific Research Corpora",
            "authors": "Dr. Alex Rivera, Dr. Kenji Tanaka, Maya Patel",
            "institution": "Institute for Data Science, Cambridge University",
            "abstract": "Dense embedding models are fundamental to semantic literature retrieval, yet a persistent trade-off exists between model scale, computational latency, and retrieval accuracy. In this investigation, we perform a comprehensive comparative benchmark evaluating lightweight Sentence Transformers (including all-MiniLM-L6-v2, BGE-small, and Snowflake-Arctic) against multi-billion parameter proprietary embedding APIs. Our empirical results demonstrate that 22-million parameter models retain 94.6% of the retrieval accuracy of 7B-parameter models while executing inference 12.8 times faster and operating locally with zero GPU memory requirements.",
            "keywords": "Sentence Transformers, all-MiniLM-L6-v2, Vector Embeddings, Semantic Search, Computational Efficiency",
            "pages": [
                """1. Introduction
The democratization of AI-powered literature review tools demands architectures that can execute locally on standard consumer workstations without requiring high-end datacenter GPUs. While billion-parameter models dominate leaderboards such as MTEB, their deployment cost and latency present major hurdles for universities and individual researchers.

2. Experimental Setup
We evaluated 8 embedding models across three academic domains: Computer Science, Medicine, and Physics.
Each corpus was chunked into uniform segments of 500 words with 50-word overlaps.
ChromaDB was deployed as the persistent vector database using cosine distance metrics.
Hardware benchmarking was conducted on standard Intel Core i7 and Apple M2 silicon.""",

                """3. Findings and Benchmark Results
Our primary findings reveal:
- Accuracy vs. Footprint: all-MiniLM-L6-v2 achieved a NDCG@10 of 0.768 across CS literature, compared to 0.812 for OpenAI text-embedding-3-large, despite being 1/50th of the computational size.
- Throughput: On standard CPU hardware, all-MiniLM-L6-v2 processed 420 sentences per second, enabling instant indexing of 100-page academic dissertations in under 8 seconds.
- Cold-Start Latency: Local ONNX-runtime acceleration reduced startup latency to under 350 milliseconds.

4. Comparative Analysis
While larger models excel in ambiguous cross-lingual queries, specialized academic vocabulary (e.g. bioinformatics gene symbols) exhibits equivalent precision across both lightweight and massive models when proper chunking heuristics are enforced.""",

                """5. Limitations and Future Work
We identify the following explicit limitations in our benchmark:
- Fixed 512-Token Context Limit: all-MiniLM-L6-v2 truncates text passages exceeding 512 tokens, occasionally dropping contextual conclusions in verbose academic prose.
- Lack of Native Multi-Lingual Pre-training: Performance drops by 23% when indexing non-English academic manuscripts.
- Domain Adaptation Gap: Zero-shot retrieval on niche quantum mechanics papers showed lower cosine separation.

Future research should explore quantized int8 ONNX representations and adaptive sliding window tokenization to support arbitrary document lengths."""
            ]
        },
        {
            "filename": "multiagent_literature_review.pdf",
            "title": "Autonomous Multi-Agent Collaboration for Automated Literature Reviews and Hypothesis Generation",
            "authors": "Prof. Arthur Pendelton, Dr. Wei Zhang, Elena Morozova",
            "institution": "Center for Collective Intelligence, Oxford University",
            "abstract": "Writing comprehensive academic literature reviews requires complex orchestrations of search, cross-paper comparison, critical critique, limitation identification, and academic prose synthesis. In this paper, we introduce LitAgent, an autonomous multi-agent framework comprising specialized sub-agents: Reader Agent, Comparator Agent, Critique Agent, and Writer Agent. Utilizing Google Gemini models combined with persistent vector memory, LitAgent produces structured 8-section literature reviews with grounded citations. In blinded expert peer evaluations by 18 faculty members, LitAgent syntheses were judged indistinguishable in rigor from graduate-level literature reviews in 78% of trials.",
            "keywords": "Multi-Agent Systems, Automated Literature Review, Gemini API, RAG, Research Gap Extraction",
            "pages": [
                """1. Introduction & Motivation
Scholarly literature reviews serve as the essential cornerstone of academic inquiry, establishing context, identifying consensus, and pointing toward unresolved gaps. However, manual synthesis across dozens of publications requires hundreds of researcher hours.
Autonomous LLM agents offer an unprecedented opportunity to automate literature analysis, provided that mechanisms for citation integrity, factual grounding, and critical reflection are strictly enforced.

2. Architectural Design of LitAgent
Our architecture decomposes literature review generation into four collaborative stages:
1. Extraction & Indexing: Reader agents extract structured metadata (title, abstract, year, methodology, metrics) and populate persistent Chroma collections.
2. Cross-Document Comparison: Comparator agents align papers along objective, dataset, algorithm, and metric axes.
3. Gap & Limitation Analyzer: Critique agents parse stated limitations and identify recurring bottlenecks across papers.
4. Publication Synthesis: Writer agents generate publication-ready academic sections with inline APA citations.""",

                """3. Empirical Evaluation
We conducted double-blind evaluations across 30 literature review drafts generated from Computer Science and Bioengineering corpora.
Reviewers evaluated papers on five criteria:
- Comprehensiveness: 4.6 / 5.0
- Citation Integrity: 4.8 / 5.0 (Zero fabricated references detected)
- Critical Synthesis: 4.2 / 5.0
- Readability & Flow: 4.5 / 5.0

Comparative analysis proved that structured agent decomposition significantly outperforms monolithic prompt generation, which frequently hallucinates citations or produces superficial generic summaries.""",

                """4. Stated Limitations
The authors note three primary limitations in the current implementation:
- Qualitative Subjectivity in Gap Identification: While explicit author limitations are extracted with high fidelity, AI-inferred research opportunities depend on prompt framing and can occasionally suggest overly speculative research directions.
- Inability to Audit Non-Textual Figures: Complex experimental graphs, schematics, and vector illustrations cannot be parsed without multi-modal visual language grounding.
- API Rate Constraints: Generating multi-stage reviews across large paper collections consumes significant LLM token bandwidth.

5. Future Research Directions
We advocate for future inquiry into automated peer review generation, interactive human-in-the-loop review editing, and integration with citation graphs (e.g. Semantic Scholar and arXiv APIs)."""
            ]
        }
    ]

    for p in papers_data:
        doc = fitz.open()
        file_path = os.path.join(output_dir, p["filename"])

        for page_idx, page_content in enumerate(p["pages"]):
            page = doc.new_page()
            
            # If first page, add title & header
            if page_idx == 0:
                header_text = f"{p['title']}\n{p['authors']}\n{p['institution']}\n\nAbstract\n{p['abstract']}\n\nKeywords: {p['keywords']}\n\n"
                full_text = header_text + page_content
            else:
                full_text = page_content

            page.insert_text((50, 60), full_text, fontsize=10)

        # Set PDF metadata
        doc.set_metadata({
            "title": p["title"],
            "author": p["authors"],
            "keywords": p["keywords"],
            "creationDate": "D:20260315120000"
        })

        doc.save(file_path)
        doc.close()
        print(f"Created sample paper: {file_path}")

if __name__ == "__main__":
    create_sample_papers()
