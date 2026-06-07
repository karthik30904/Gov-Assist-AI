from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi

from models import SchemeChunk


@dataclass
class RetrievalResult:
    chunk: SchemeChunk
    score: float
    source: str


class HybridRetriever:
    def __init__(self, chunks: list[SchemeChunk], embeddings: np.ndarray | None = None) -> None:
        self.chunks = chunks
        self.embeddings = embeddings
        self.bm25 = BM25Okapi([chunk.text.lower().split() for chunk in chunks]) if chunks else None

    def search(self, query: str, query_embedding: np.ndarray | None = None, top_k: int = 5) -> list[RetrievalResult]:
        scores: dict[int, float] = {}

        if self.bm25:
            for idx, score in enumerate(self.bm25.get_scores(query.lower().split())):
                scores[idx] = scores.get(idx, 0.0) + float(score)

        if self.embeddings is not None and query_embedding is not None and len(self.embeddings):
            vector_scores = self._cosine_scores(query_embedding)
            for idx, score in enumerate(vector_scores):
                scores[idx] = scores.get(idx, 0.0) + float(score)

        ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [RetrievalResult(chunk=self.chunks[idx], score=score, source="hybrid") for idx, score in ranked]

    def quality_sufficient(self, results: list[RetrievalResult], threshold: float = 0.55) -> bool:
        return bool(results) and max(result.score for result in results) >= threshold

    def _cosine_scores(self, query_embedding: np.ndarray) -> np.ndarray:
        query = query_embedding / max(np.linalg.norm(query_embedding), 1e-9)
        corpus = self.embeddings / np.maximum(np.linalg.norm(self.embeddings, axis=1, keepdims=True), 1e-9)
        return corpus @ query
