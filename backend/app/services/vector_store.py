import gc
import json
import logging
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.database import SessionLocal, is_postgres
from app.models import Paper, PaperChunk
from app.services.embedding_service import embedding_service
from app.services.pdf_service import PDFService

logger = logging.getLogger("researchmate.vector_store")


def _cosine_distance(vec_a: List[float], vec_b: List[float]) -> float:
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 1.0
    return 1.0 - (dot / (norm_a * norm_b))


def _serialize_embedding(vec: List[float]):
    return vec if is_postgres else json.dumps(vec)


def _deserialize_embedding(val) -> Optional[List[float]]:
    if val is None:
        return None
    if isinstance(val, str):
        return json.loads(val)
    return list(val)


class VectorStoreService:
    """
    Vector store backed by Supabase PostgreSQL + pgvector.
    Uses external Gemini embeddings (gemini-embedding-001) and SQL vector similarity search.
    """

    def add_paper_chunks(
        self,
        project_id: int,
        paper_id: int,
        paper_title: str,
        chunks: List[Dict[str, Any]],
        db: Optional[Session] = None,
    ):
        """
        Embed chunks via external Gemini API in small bounded batches and persist
        them to PostgreSQL (pgvector) with model & dimensionality metadata.
        """
        if not chunks:
            return

        # Defensive sanitization: strip NUL bytes and skip empty chunks before DB insertion
        sanitized_chunks: List[Dict[str, Any]] = []
        for ch in chunks:
            clean_content = PDFService.sanitize_text(ch.get("content")).strip()
            if not clean_content:
                continue
            sanitized_chunks.append({**ch, "content": clean_content})

        if not sanitized_chunks:
            return

        owns_session = db is None
        session = db or SessionLocal()
        batch_size = embedding_service.batch_size

        try:
            # Remove any stale chunks for this paper idempotently
            session.query(PaperChunk).filter(PaperChunk.paper_id == int(paper_id)).delete(
                synchronize_session=False
            )

            for i in range(0, len(sanitized_chunks), batch_size):
                batch = sanitized_chunks[i : i + batch_size]
                texts = [c["content"] for c in batch]
                vectors = embedding_service.embed_documents(texts)

                chunk_rows = []
                for ch, vec in zip(batch, vectors):
                    chunk_rows.append(
                        PaperChunk(
                            paper_id=int(paper_id),
                            project_id=int(project_id),
                            chunk_index=int(ch["chunk_index"]),
                            page_number=int(ch["page_number"]),
                            content=ch["content"],
                            token_count=int(ch.get("token_count", 0)),
                            embedding_model=embedding_service.model_name,
                            embedding_dimensions=embedding_service.dimensions,
                            embedding=_serialize_embedding(vec),
                        )
                    )
                session.bulk_save_objects(chunk_rows)
                session.flush()

            if owns_session:
                session.commit()
        except Exception:
            if owns_session:
                session.rollback()
            raise
        finally:
            if owns_session:
                session.close()
            gc.collect()

    def _query_subset(
        self,
        session: Session,
        project_id: int,
        query_embedding: List[float],
        limit: int,
        paper_ids: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        if is_postgres:
            distance_expr = PaperChunk.embedding.cosine_distance(query_embedding).label("distance")
            q = (
                session.query(PaperChunk, Paper.title, distance_expr)
                .join(Paper, PaperChunk.paper_id == Paper.id)
                .filter(
                    Paper.project_id == int(project_id),
                    PaperChunk.embedding.isnot(None),
                    PaperChunk.embedding_model == embedding_service.model_name,
                )
            )
            if paper_ids:
                q = q.filter(PaperChunk.paper_id.in_([int(pid) for pid in paper_ids]))

            rows = q.order_by(distance_expr).limit(limit).all()
            return [
                {
                    "content": chunk.content,
                    "paper_id": chunk.paper_id,
                    "paper_title": paper_title or "Unknown Paper",
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "distance": float(distance) if distance is not None else 1.0,
                }
                for chunk, paper_title, distance in rows
            ]

        # SQLite local-test fallback (still uses real/mocked external embeddings, never local model)
        q = (
            session.query(PaperChunk, Paper.title)
            .join(Paper, PaperChunk.paper_id == Paper.id)
            .filter(
                Paper.project_id == int(project_id),
                PaperChunk.embedding.isnot(None),
                PaperChunk.embedding_model == embedding_service.model_name,
            )
        )
        if paper_ids:
            q = q.filter(PaperChunk.paper_id.in_([int(pid) for pid in paper_ids]))

        scored = []
        for chunk, paper_title in q.all():
            vec = _deserialize_embedding(chunk.embedding)
            if not vec:
                continue
            dist = _cosine_distance(query_embedding, vec)
            scored.append(
                {
                    "content": chunk.content,
                    "paper_id": chunk.paper_id,
                    "paper_title": paper_title or "Unknown Paper",
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "distance": float(dist),
                }
            )
        scored.sort(key=lambda x: x["distance"])
        return scored[:limit]

    def query_chunks(
        self,
        project_id: int,
        query: str,
        n_results: int = 6,
        paper_ids: Optional[List[int]] = None,
        db: Optional[Session] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top matching chunks for a project query using pgvector cosine similarity
        with multi-document source diversity.
        """
        owns_session = db is None
        session = db or SessionLocal()

        try:
            query_embedding = embedding_service.embed_query(query)

            # Case 1: Multiple papers explicitly selected -> Apply source diversity
            if paper_ids and len(paper_ids) > 1:
                per_paper_k = max(2, min(4, max(2, n_results // len(paper_ids))))
                combined_chunks: List[Dict[str, Any]] = []
                seen_chunk_keys = set()

                for pid in paper_ids:
                    for item in self._query_subset(
                        session, project_id, query_embedding, limit=per_paper_k, paper_ids=[int(pid)]
                    ):
                        key = (item["paper_id"], item["chunk_index"])
                        if key not in seen_chunk_keys:
                            seen_chunk_keys.add(key)
                            combined_chunks.append(item)

                for item in self._query_subset(
                    session, project_id, query_embedding, limit=n_results, paper_ids=[int(p) for p in paper_ids]
                ):
                    key = (item["paper_id"], item["chunk_index"])
                    if key not in seen_chunk_keys:
                        seen_chunk_keys.add(key)
                        combined_chunks.append(item)

                combined_chunks.sort(key=lambda x: x.get("distance", 1.0))
                return combined_chunks[: max(n_results, len(paper_ids) * 2)]

            # Case 2: Single paper or global project query
            return self._query_subset(
                session,
                project_id,
                query_embedding,
                limit=n_results,
                paper_ids=[int(paper_ids[0])] if paper_ids and len(paper_ids) == 1 else None,
            )
        finally:
            if owns_session:
                session.close()

    def delete_paper_chunks(self, project_id: int, paper_id: int, db: Optional[Session] = None):
        """Remove all chunks associated with a specific paper."""
        owns_session = db is None
        session = db or SessionLocal()
        try:
            session.query(PaperChunk).filter(PaperChunk.paper_id == int(paper_id)).delete(
                synchronize_session=False
            )
            if owns_session:
                session.commit()
        except Exception as e:
            if owns_session:
                session.rollback()
            logger.warning(f"Error deleting chunks for paper {paper_id}: {e}")
        finally:
            if owns_session:
                session.close()

    def delete_project_collection(self, project_id: int, db: Optional[Session] = None):
        """Delete all vector chunks associated with a project."""
        owns_session = db is None
        session = db or SessionLocal()
        try:
            paper_ids = [
                row[0] for row in session.query(Paper.id).filter(Paper.project_id == int(project_id)).all()
            ]
            if paper_ids:
                session.query(PaperChunk).filter(PaperChunk.paper_id.in_(paper_ids)).delete(
                    synchronize_session=False
                )
            if owns_session:
                session.commit()
        except Exception as e:
            if owns_session:
                session.rollback()
            logger.warning(f"Error deleting vectors for project {project_id}: {e}")
        finally:
            if owns_session:
                session.close()


vector_store = VectorStoreService()
