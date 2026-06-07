from __future__ import annotations

from pathlib import Path

import numpy as np

from models import SchemeChunk


class LocalVectorStore:
    def __init__(self, path: Path = Path("data/vector_store.npz")) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, chunks: list[SchemeChunk], embeddings: np.ndarray) -> None:
        np.savez_compressed(
            self.path,
            embeddings=embeddings,
            chunks=np.array([chunk.model_dump_json() for chunk in chunks], dtype=object),
        )

    def load(self) -> tuple[list[SchemeChunk], np.ndarray]:
        if not self.path.exists():
            return [], np.array([])
        data = np.load(self.path, allow_pickle=True)
        chunks = [SchemeChunk.model_validate_json(raw) for raw in data["chunks"]]
        return chunks, data["embeddings"]
