from __future__ import annotations

from typing import List, Optional

# Lazy import to avoid heavy cost at import time
_SMODEL = None

def _get_model(model_name: str):
    global _SMODEL
    if _SMODEL is None:
        from sentence_transformers import SentenceTransformer
        _SMODEL = SentenceTransformer(model_name)
    return _SMODEL


class EmbeddingProvider:
    """
    Simple embedding provider using sentence-transformers.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        self.model_name = model_name

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        model = _get_model(self.model_name)
        # Normalize embeddings for cosine similarity
        embs = model.encode(texts, normalize_embeddings=True).tolist()
        return embs

    def embed_query(self, text: str) -> List[float]:
        return self.embed_texts([text])[0]