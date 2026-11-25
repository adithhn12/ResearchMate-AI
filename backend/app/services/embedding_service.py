import logging
from typing import List
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger("researchmate.embeddings")


class ExternalEmbeddingService:
    """
    Generates text embeddings exclusively via Google's external Gemini Embedding API
    (gemini-embedding-001) using the official google-genai SDK.
    Never falls back to local ONNX or Sentence Transformers inference.
    """

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME or "gemini-embedding-001"
        self.dimensions = int(settings.EMBEDDING_DIMENSIONS or 768)
        self.batch_size = max(1, min(32, int(settings.EMBEDDING_BATCH_SIZE or 16)))
        self._client = None

    def _get_client(self) -> genai.Client:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. External embeddings require a valid Gemini API key."
            )
        if self._client is None:
            self._client = genai.Client(api_key=api_key)
        return self._client

    def _embed_batch(self, texts: List[str], task_type: str) -> List[List[float]]:
        client = self._get_client()
        config = types.EmbedContentConfig(
            output_dimensionality=self.dimensions,
            task_type=task_type,
        )
        response = client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config=config,
        )
        embeddings = getattr(response, "embeddings", None) or []
        if len(embeddings) != len(texts):
            raise RuntimeError(
                f"Embedding API returned {len(embeddings)} vectors for {len(texts)} inputs."
            )

        vectors: List[List[float]] = []
        for emb in embeddings:
            vals = list(emb.values)
            if len(vals) != self.dimensions:
                raise RuntimeError(
                    f"Expected {self.dimensions}-d embedding from {self.model_name}, got {len(vals)}."
                )
            vectors.append(vals)
        return vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate document embeddings in small bounded batches."""
        if not texts:
            return []
        all_vectors: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            all_vectors.extend(self._embed_batch(batch, task_type="RETRIEVAL_DOCUMENT"))
        return all_vectors

    def embed_query(self, text: str) -> List[float]:
        """Generate a query embedding using the exact same model and dimensionality."""
        cleaned = (text or "").strip()
        if not cleaned:
            raise ValueError("Query text for embedding cannot be empty.")
        return self._embed_batch([cleaned], task_type="RETRIEVAL_QUERY")[0]


embedding_service = ExternalEmbeddingService()
