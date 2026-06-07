from __future__ import annotations

from models import Scheme, SchemeChunk

from .chunking import chunk_scheme
from .embeddings import EmbeddingModel
from .vector_store import LocalVectorStore


class KnowledgeIndexer:
    def __init__(
        self,
        embedding_model: EmbeddingModel | None = None,
        vector_store: LocalVectorStore | None = None,
    ) -> None:
        self.embedding_model = embedding_model or EmbeddingModel()
        self.vector_store = vector_store or LocalVectorStore()

    def index(self, schemes: list[Scheme]) -> list[SchemeChunk]:
        chunks = [chunk for scheme in schemes for chunk in chunk_scheme(scheme)]
        embeddings = self.embedding_model.embed_chunks(chunks)
        self.vector_store.save(chunks, embeddings)
        return chunks
