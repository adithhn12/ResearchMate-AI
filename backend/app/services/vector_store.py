import gc
import logging
import os
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, cast

# Constrain thread pools and memory arenas BEFORE importing onnxruntime / chromadb
# to stay well within Render free-instance (512 MB) memory limits.
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("ORT_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import chromadb
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from app.config import settings, BASE_DIR

logger = logging.getLogger("researchmate.vector_store")

_MODEL_LOCK = threading.Lock()
_ONNX_SESSION = None
_TOKENIZER = None
_MODEL_DIR: Optional[Path] = None


def _resolve_model_dir() -> Path:
    """
    Resolve the directory containing the extracted all-MiniLM-L6-v2 ONNX files.
    Checks:
      1. Project-local .model_cache (populated during Render buildCommand)
      2. Standard ChromaDB user cache (~/.cache/chroma/onnx_models/all-MiniLM-L6-v2)
      3. Falls back to downloading once into project-local .model_cache
    """
    global _MODEL_DIR
    if _MODEL_DIR is not None:
        return _MODEL_DIR

    required_files = ("model.onnx", "tokenizer.json")
    candidates = [
        BASE_DIR / ".model_cache" / "all-MiniLM-L6-v2" / "onnx",
        Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2" / "onnx",
    ]
    for candidate in candidates:
        if all((candidate / f).exists() for f in required_files):
            _MODEL_DIR = candidate
            return _MODEL_DIR

    # Download once using ChromaDB's built-in downloader into BASE_DIR/.model_cache
    from chromadb.utils.embedding_functions.onnx_mini_lm_l6_v2 import ONNXMiniLM_L6_V2

    target_parent = BASE_DIR / ".model_cache" / "all-MiniLM-L6-v2"
    target_parent.mkdir(parents=True, exist_ok=True)
    downloader = ONNXMiniLM_L6_V2()
    downloader.DOWNLOAD_PATH = target_parent
    downloader._download_model_if_not_exists()
    _MODEL_DIR = target_parent / downloader.EXTRACTED_FOLDER_NAME
    return _MODEL_DIR


def _get_onnx_runtime_and_tokenizer():
    """
    Initialize and return the process-wide singleton ONNX InferenceSession and Tokenizer.
    Thread-safe and guaranteed to load the model into memory only once.
    """
    global _ONNX_SESSION, _TOKENIZER
    if _ONNX_SESSION is not None and _TOKENIZER is not None:
        return _ONNX_SESSION, _TOKENIZER

    with _MODEL_LOCK:
        if _ONNX_SESSION is not None and _TOKENIZER is not None:
            return _ONNX_SESSION, _TOKENIZER

        import onnxruntime as ort
        from tokenizers import Tokenizer

        model_dir = _resolve_model_dir()
        logger.info(f"Initializing singleton all-MiniLM-L6-v2 ONNX session from {model_dir}")

        so = ort.SessionOptions()
        so.log_severity_level = 3
        so.intra_op_num_threads = 1
        so.inter_op_num_threads = 1
        so.enable_cpu_mem_arena = False
        so.enable_mem_pattern = False
        so.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        session = ort.InferenceSession(
            str(model_dir / "model.onnx"),
            providers=["CPUExecutionProvider"],
            sess_options=so,
        )

        tokenizer = Tokenizer.from_file(str(model_dir / "tokenizer.json"))
        tokenizer.enable_truncation(max_length=256)
        # Dynamic padding (no fixed length=256) avoids wasting RAM on short queries/chunks
        tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")

        _ONNX_SESSION = session
        _TOKENIZER = tokenizer
        logger.info("Singleton all-MiniLM-L6-v2 ONNX session initialized successfully")
        return _ONNX_SESSION, _TOKENIZER


class SingletonMiniLMEmbeddingFunction(EmbeddingFunction[Documents]):
    """
    Memory-optimised singleton embedding function for all-MiniLM-L6-v2.
    Reuses a single ONNX Runtime session and processes small micro-batches
    so peak RSS stays safe on 512 MB cloud instances.
    """

    def __init__(self, embed_batch_size: int = 16):
        self.embed_batch_size = embed_batch_size

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []

        session, tokenizer = _get_onnx_runtime_and_tokenizer()
        all_embeddings: List[np.ndarray] = []

        for i in range(0, len(input), self.embed_batch_size):
            batch = list(input[i : i + self.embed_batch_size])
            encoded = tokenizer.encode_batch(batch)

            input_ids = np.array([e.ids for e in encoded], dtype=np.int64)
            attention_mask = np.array([e.attention_mask for e in encoded], dtype=np.int64)
            token_type_ids = np.zeros_like(input_ids, dtype=np.int64)

            last_hidden_state = session.run(
                None,
                {
                    "input_ids": input_ids,
                    "attention_mask": attention_mask,
                    "token_type_ids": token_type_ids,
                },
            )[0]

            # Mean pooling with attention mask
            input_mask_expanded = np.broadcast_to(
                np.expand_dims(attention_mask, -1), last_hidden_state.shape
            )
            sum_embeddings = np.sum(last_hidden_state * input_mask_expanded, axis=1)
            sum_mask = np.clip(input_mask_expanded.sum(axis=1), a_min=1e-9, a_max=None)
            embeddings = sum_embeddings / sum_mask

            # L2 normalize
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            norms[norms == 0] = 1e-12
            embeddings = (embeddings / norms).astype(np.float32)

            all_embeddings.extend(embeddings)

        return cast(Embeddings, all_embeddings)

    @staticmethod
    def name() -> str:
        return "default"

    def get_config(self) -> Dict[str, Any]:
        return {}

    @staticmethod
    def build_from_config(config: Dict[str, Any]) -> "SingletonMiniLMEmbeddingFunction":
        return SingletonMiniLMEmbeddingFunction()

    def max_tokens(self) -> int:
        return 256


class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        self.embedding_fn = SingletonMiniLMEmbeddingFunction(embed_batch_size=16)

    def warmup_if_cached(self) -> None:
        """Warm up the singleton ONNX session at startup if model files are already on disk."""
        candidates = [
            BASE_DIR / ".model_cache" / "all-MiniLM-L6-v2" / "onnx",
            Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2" / "onnx",
        ]
        if any((c / "model.onnx").exists() and (c / "tokenizer.json").exists() for c in candidates):
            _get_onnx_runtime_and_tokenizer()

    def get_collection(self, project_id: int):
        """Get or create a dedicated ChromaDB collection for a research project."""
        collection_name = f"research_project_{project_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"project_id": str(project_id)},
        )

    def add_paper_chunks(self, project_id: int, paper_id: int, paper_title: str, chunks: List[Dict[str, Any]]):
        """
        Store chunk embeddings with metadata in small batches to bound peak memory.
        chunks: [{"chunk_index": int, "page_number": int, "content": str}]
        """
        if not chunks:
            return

        collection = self.get_collection(project_id)

        batch_size = 16
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            ids = [
                f"paper_{paper_id}_p{chunk['page_number']}_c{chunk['chunk_index']}"
                for chunk in batch
            ]
            documents = [chunk["content"] for chunk in batch]
            metadatas = [
                {
                    "paper_id": int(paper_id),
                    "paper_title": str(paper_title),
                    "page_number": int(chunk["page_number"]),
                    "chunk_index": int(chunk["chunk_index"]),
                }
                for chunk in batch
            ]
            collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

        gc.collect()

    def query_chunks(
        self,
        project_id: int,
        query: str,
        n_results: int = 6,
        paper_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top matching chunks for a project query with source diversity.
        When multiple papers are selected, balanced chunks are retrieved from each
        selected paper to prevent a single document from dominating the context.
        """
        collection = self.get_collection(project_id)
        total_docs = collection.count()
        if total_docs == 0:
            return []

        # Case 1: Multiple papers explicitly selected -> Apply source diversity
        if paper_ids and len(paper_ids) > 1:
            per_paper_k = max(2, min(4, max(2, n_results // len(paper_ids))))
            combined_chunks = []
            seen_chunk_keys = set()

            # Compute query embedding once and reuse across all per-paper queries
            query_embedding = self.embedding_fn([query])[0].tolist()

            for pid in paper_ids:
                try:
                    res = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=per_paper_k,
                        where={"paper_id": int(pid)},
                    )
                    if res and "documents" in res and len(res["documents"]) > 0:
                        docs = res["documents"][0]
                        metas = res["metadatas"][0] if "metadatas" in res else [{}] * len(docs)
                        distances = res["distances"][0] if "distances" in res else [0.0] * len(docs)
                        for doc, meta, dist in zip(docs, metas, distances):
                            chunk_key = (meta.get("paper_id"), meta.get("chunk_index"))
                            if chunk_key not in seen_chunk_keys:
                                seen_chunk_keys.add(chunk_key)
                                combined_chunks.append({
                                    "content": doc,
                                    "paper_id": meta.get("paper_id"),
                                    "paper_title": meta.get("paper_title", "Unknown Paper"),
                                    "page_number": meta.get("page_number", 1),
                                    "chunk_index": meta.get("chunk_index", 0),
                                    "distance": dist,
                                })
                except Exception as e:
                    logger.warning(f"Error querying chunks for paper {pid}: {e}")

            try:
                global_where = {"paper_id": {"$in": [int(pid) for pid in paper_ids]}}
                res_global = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, total_docs),
                    where=global_where,
                )
                if res_global and "documents" in res_global and len(res_global["documents"]) > 0:
                    g_docs = res_global["documents"][0]
                    g_metas = res_global["metadatas"][0] if "metadatas" in res_global else [{}] * len(g_docs)
                    g_distances = res_global["distances"][0] if "distances" in res_global else [0.0] * len(g_docs)
                    for doc, meta, dist in zip(g_docs, g_metas, g_distances):
                        chunk_key = (meta.get("paper_id"), meta.get("chunk_index"))
                        if chunk_key not in seen_chunk_keys:
                            seen_chunk_keys.add(chunk_key)
                            combined_chunks.append({
                                "content": doc,
                                "paper_id": meta.get("paper_id"),
                                "paper_title": meta.get("paper_title", "Unknown Paper"),
                                "page_number": meta.get("page_number", 1),
                                "chunk_index": meta.get("chunk_index", 0),
                                "distance": dist,
                            })
            except Exception as e:
                logger.warning(f"Global query fallback error: {e}")

            combined_chunks.sort(key=lambda x: x.get("distance", 1.0))
            return combined_chunks[: max(n_results, len(paper_ids) * 2)]

        # Case 2: Single paper or global project query
        where_filter = None
        if paper_ids and len(paper_ids) == 1:
            where_filter = {"paper_id": int(paper_ids[0])}

        actual_n = min(n_results, total_docs)
        results = collection.query(
            query_texts=[query],
            n_results=actual_n,
            where=where_filter,
        )

        retrieved = []
        if results and "documents" in results and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                retrieved.append({
                    "content": doc,
                    "paper_id": meta.get("paper_id"),
                    "paper_title": meta.get("paper_title", "Unknown Paper"),
                    "page_number": meta.get("page_number", 1),
                    "chunk_index": meta.get("chunk_index", 0),
                    "distance": dist,
                })

        return retrieved

    def delete_paper_chunks(self, project_id: int, paper_id: int):
        """Remove all chunks associated with a specific paper."""
        try:
            collection = self.get_collection(project_id)
            collection.delete(where={"paper_id": int(paper_id)})
        except Exception as e:
            logger.warning(f"Error deleting chunks for paper {paper_id}: {e}")

    def delete_project_collection(self, project_id: int):
        """Delete an entire project's vector collection."""
        try:
            collection_name = f"research_project_{project_id}"
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            logger.warning(f"Error deleting collection for project {project_id}: {e}")


vector_store = VectorStoreService()
