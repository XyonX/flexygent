from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np


@dataclass
class SearchResult:
    text: str
    metadata: Dict[str, object]
    score: float


class LocalNumpyVectorStore:
    """
    A lightweight local vector store.

    Files in index_dir:
      - embeddings.npy  (float32, shape [N, D])
      - meta.jsonl      (N lines; each JSON with {"text": str, "metadata": dict})

    Cosine similarity search using normalized embeddings.
    """

    def __init__(self, index_dir: str) -> None:
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)
        self.emb_path = os.path.join(self.index_dir, "embeddings.npy")
        self.meta_path = os.path.join(self.index_dir, "meta.jsonl")

        self._emb: np.ndarray = np.zeros((0, 0), dtype=np.float32)
        self._meta: List[Dict[str, object]] = []

        self._loaded = False

    def _load(self) -> None:
        if self._loaded:
            return
        if os.path.exists(self.emb_path):
            self._emb = np.load(self.emb_path).astype(np.float32, copy=False)
        else:
            self._emb = np.zeros((0, 0), dtype=np.float32)

        if os.path.exists(self.meta_path):
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self._meta = [json.loads(line) for line in f if line.strip()]
        else:
            self._meta = []
        self._loaded = True

    def add(self, embeddings: List[List[float]], items: List[Dict[str, object]]) -> int:
        """
        Append embeddings and their corresponding items (each item must contain keys: text, metadata).
        Returns number of items added.
        """
        self._load()
        if not embeddings:
            return 0

        new_emb = np.array(embeddings, dtype=np.float32)
        if self._emb.size == 0:
            self._emb = new_emb
        else:
            if self._emb.shape[1] != new_emb.shape[1]:
                raise ValueError(f"Embedding dimension mismatch: have {self._emb.shape[1]}, new {new_emb.shape[1]}")
            self._emb = np.vstack([self._emb, new_emb])

        # Append metadata lines
        with open(self.meta_path, "a", encoding="utf-8") as f:
            for it in items:
                f.write(json.dumps({"text": it["text"], "metadata": it.get("metadata", {})}, ensure_ascii=False) + "\n")
        # Refresh _meta in memory by reading only new items
        self._meta.extend(items)

        # Persist embeddings
        np.save(self.emb_path, self._emb)
        return len(items)

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[SearchResult]:
        self._load()
        if self._emb.size == 0:
            return []

        q = np.array(query_embedding, dtype=np.float32)
        if q.ndim == 1:
            q = q[None, :]

        # Both embeddings and query are expected normalized -> cosine similarity = dot product
        sims = (self._emb @ q.T).squeeze(-1)  # shape [N]
        if sims.ndim == 0:
            sims = np.array([float(sims)])

        top_k = max(1, min(int(top_k), sims.shape[0]))
        idxs = np.argpartition(-sims, top_k - 1)[:top_k]
        # sort selected by score
        idxs = idxs[np.argsort(-sims[idxs])]

        results: List[SearchResult] = []
        for i in idxs:
            meta = self._meta[i]
            results.append(
                SearchResult(
                    text=str(meta["text"]),
                    metadata=dict(meta.get("metadata") or {}),
                    score=float(sims[i]),
                )
            )
        return results