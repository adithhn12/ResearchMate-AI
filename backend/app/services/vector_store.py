import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from app.config import settings

class VectorStoreService:
    def __init__(self):
        self.persist_directory = settings.CHROMA_PERSIST_DIR
        os.makedirs(self.persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # Use ChromaDB's ONNX-accelerated all-MiniLM-L6-v2 DefaultEmbeddingFunction
        # This provides the exact requested all-MiniLM-L6-v2 embeddings reliably and swiftly
        self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

    def get_collection(self, project_id: int):
        """Get or create a dedicated ChromaDB collection for a research project."""
        collection_name = f"research_project_{project_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"project_id": str(project_id)}
        )

    def add_paper_chunks(self, project_id: int, paper_id: int, paper_title: str, chunks: List[Dict[str, Any]]):
        """
        Store chunk embeddings with metadata.
        chunks: [{"chunk_index": int, "page_number": int, "content": str}]
        """
        if not chunks:
            return

        collection = self.get_collection(project_id)
        
        ids = []
        documents = []
        metadatas = []
        
        for chunk in chunks:
            chunk_id = f"paper_{paper_id}_p{chunk['page_number']}_c{chunk['chunk_index']}"
            ids.append(chunk_id)
            documents.append(chunk["content"])
            metadatas.append({
                "paper_id": int(paper_id),
                "paper_title": str(paper_title),
                "page_number": int(chunk["page_number"]),
                "chunk_index": int(chunk["chunk_index"])
            })
            
        # Add in batches of 100 for efficiency
        batch_size = 100
        for i in range(0, len(ids), batch_size):
            collection.upsert(
                ids=ids[i:i + batch_size],
                documents=documents[i:i + batch_size],
                metadatas=metadatas[i:i + batch_size]
            )

    def query_chunks(
        self,
        project_id: int,
        query: str,
        n_results: int = 6,
        paper_ids: Optional[List[int]] = None
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

            # Retrieve top chunks from EACH selected paper
            for pid in paper_ids:
                try:
                    res = collection.query(
                        query_texts=[query],
                        n_results=per_paper_k,
                        where={"paper_id": int(pid)}
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
                                    "distance": dist
                                })
                except Exception as e:
                    print(f"Error querying chunks for paper {pid}: {e}")

            # Also run a global query across all selected papers for strongest global matches
            try:
                global_where = {"paper_id": {"$in": [int(pid) for pid in paper_ids]}}
                res_global = collection.query(
                    query_texts=[query],
                    n_results=min(n_results, total_docs),
                    where=global_where
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
                                "distance": dist
                            })
            except Exception as e:
                print(f"Global query fallback error: {e}")

            # Sort by distance (lower is closer/more relevant)
            combined_chunks.sort(key=lambda x: x.get("distance", 1.0))
            return combined_chunks[:max(n_results, len(paper_ids) * 2)]

        # Case 2: Single paper or global project query
        where_filter = None
        if paper_ids and len(paper_ids) == 1:
            where_filter = {"paper_id": int(paper_ids[0])}

        actual_n = min(n_results, total_docs)
        results = collection.query(
            query_texts=[query],
            n_results=actual_n,
            where=where_filter
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
                    "distance": dist
                })
                
        return retrieved

    def delete_paper_chunks(self, project_id: int, paper_id: int):
        """Remove all chunks associated with a specific paper."""
        try:
            collection = self.get_collection(project_id)
            collection.delete(where={"paper_id": int(paper_id)})
        except Exception as e:
            print(f"Error deleting chunks for paper {paper_id}: {e}")

    def delete_project_collection(self, project_id: int):
        """Delete an entire project's vector collection."""
        try:
            collection_name = f"research_project_{project_id}"
            self.client.delete_collection(name=collection_name)
        except Exception as e:
            print(f"Error deleting collection for project {project_id}: {e}")

vector_store = VectorStoreService()
