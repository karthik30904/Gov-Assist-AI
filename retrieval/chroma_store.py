from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

from models import SchemeChunk


class ChromaSchemeStore:
    def __init__(
        self,
        persist_directory: Path = Path("data/chroma"),
        collection_name: str = "myscheme_schemes",
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        persist_directory.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_directory))
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
            metadata={"source": "myscheme.gov.in"},
        )

    def count(self) -> int:
        return self.collection.count()

    def upsert_chunks(self, chunks: list[SchemeChunk]) -> None:
        if not chunks:
            return

        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            metadatas=[self._clean_metadata(chunk) for chunk in chunks],
        )

    def query(self, query: str, top_k: int = 8) -> list[dict[str, Any]]:
        if self.count() == 0:
            return []

        results = self.collection.query(query_texts=[query], n_results=top_k)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        output: list[dict[str, Any]] = []
        for idx, document in enumerate(documents):
            distance = distances[idx] if idx < len(distances) else None
            score = 1.0 / (1.0 + float(distance)) if distance is not None else 0.0
            metadata = metadatas[idx] if idx < len(metadatas) else {}
            output.append(
                {
                    "id": ids[idx] if idx < len(ids) else None,
                    "text": document,
                    "score": score,
                    "metadata": metadata,
                    "source_url": metadata.get("source_url"),
                    "scheme_name": metadata.get("scheme_name"),
                    "section": metadata.get("section"),
                }
            )
        return output

    def _clean_metadata(self, chunk: SchemeChunk) -> dict[str, str | int | float | bool]:
        metadata = {
            "scheme_name": chunk.scheme_name,
            "source_url": str(chunk.source_url),
            "section": chunk.section,
        }
        for key, value in chunk.metadata.items():
            if value is not None and isinstance(value, (str, int, float, bool)):
                metadata[key] = value
        return metadata
