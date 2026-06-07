from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from crawler import MySchemeCrawler
from llm import QwenClient
from models import Scheme
from retrieval import ChromaSchemeStore, chunk_scheme
from storage import JsonSchemeStore


@dataclass
class RagAnswer:
    answer: str
    sources: list[str]
    crawled: int
    retrieved: int
    model_used: str
    llm_used: bool
    warning: str | None = None


class SchemeRagService:
    def __init__(
        self,
        scheme_store: JsonSchemeStore | None = None,
        vector_store: ChromaSchemeStore | None = None,
        crawler: MySchemeCrawler | None = None,
        llm: QwenClient | None = None,
        crawl_timeout_seconds: int = 75,
    ) -> None:
        self.scheme_store = scheme_store or JsonSchemeStore(Path("data/schemes.jsonl"))
        self.vector_store = vector_store or ChromaSchemeStore()
        self.crawler = crawler or MySchemeCrawler(store=self.scheme_store)
        self.llm = llm or QwenClient(model="qwen2.5:14b")
        self.crawl_timeout_seconds = crawl_timeout_seconds

    async def answer(self, query: str, top_k: int = 8) -> RagAnswer:
        await self._ensure_indexed()
        results = self.vector_store.query(query, top_k=top_k)

        crawled = 0
        warning = None
        if self._needs_fresh_research(results):
            try:
                schemes = await asyncio.wait_for(
                    self.crawler.crawl(query=query, limit=12),
                    timeout=self.crawl_timeout_seconds,
                )
                crawled = len(schemes)
                self._index_schemes(schemes)
            except TimeoutError:
                warning = (
                    f"Fresh myScheme crawl timed out after {self.crawl_timeout_seconds}s. "
                    "I answered from the evidence already indexed in ChromaDB."
                )
            results = self.vector_store.query(query, top_k=top_k)

        if not results:
            return RagAnswer(
                answer=(
                    "I could not find reliable myScheme evidence in ChromaDB for this question yet.\n\n"
                    "Please run ingestion first:\n\n"
                    "`uv run python scripts/ingest_myscheme.py --query \"student scholarship\" --limit 50`\n\n"
                    "Then ask again. This prevents me from inventing an answer without official evidence."
                ),
                sources=[],
                crawled=crawled,
                retrieved=0,
                model_used=self.llm.model,
                llm_used=False,
                warning=warning,
            )

        llm_result = await self.llm.generate_grounded_answer(query=query, evidence=results)
        if llm_result.text:
            return RagAnswer(
                answer=llm_result.text,
                sources=self._sources(results),
                crawled=crawled,
                retrieved=len(results),
                model_used=llm_result.model,
                llm_used=True,
                warning=warning,
            )

        fallback = self._compose_answer(query, results)
        warning = self._join_warnings(warning, llm_result.error)
        return RagAnswer(
            answer=fallback,
            sources=self._sources(results),
            crawled=crawled,
            retrieved=len(results),
            model_used=llm_result.model,
            llm_used=False,
            warning=warning,
        )

    async def ingest(self, query: str | None = None, limit: int = 100) -> int:
        schemes = await self.crawler.crawl(query=query, limit=limit)
        self._index_schemes(schemes)
        return len(schemes)

    async def _ensure_indexed(self) -> None:
        if self.vector_store.count() > 0:
            return
        schemes = self.scheme_store.all()
        if schemes:
            self._index_schemes(schemes)

    def _index_schemes(self, schemes: list[Scheme]) -> None:
        chunks = [chunk for scheme in schemes for chunk in chunk_scheme(scheme)]
        self.vector_store.upsert_chunks(chunks)

    def _needs_fresh_research(self, results: list[dict[str, Any]]) -> bool:
        if not results:
            return True
        best_score = max(float(item.get("score", 0.0)) for item in results)
        return best_score < 0.45

    def _compose_answer(self, query: str, results: list[dict[str, Any]]) -> str:
        grouped: dict[str, dict[str, Any]] = {}
        for item in results:
            scheme_name = item.get("scheme_name") or "Relevant Scheme"
            section = item.get("section") or "evidence"
            grouped.setdefault(
                scheme_name,
                {
                    "score": 0.0,
                    "source_url": item.get("source_url"),
                    "sections": {},
                },
            )
            grouped[scheme_name]["score"] = max(grouped[scheme_name]["score"], float(item.get("score", 0.0)))
            grouped[scheme_name]["sections"].setdefault(section, []).append(item.get("text", ""))

        ranked = sorted(grouped.items(), key=lambda item: item[1]["score"], reverse=True)[:3]
        lines = [
            f"Here is the best grounded answer I found for: {query}",
            "",
        ]

        for index, (scheme_name, data) in enumerate(ranked, start=1):
            confidence = self._confidence_label(float(data["score"]))
            lines.append(f"{index}. {scheme_name} ({confidence})")
            lines.extend(self._section_lines("Overview", data["sections"].get("overview", []), limit=1))
            lines.extend(self._section_lines("Why it matches", data["sections"].get("eligibility", []), limit=2))
            lines.extend(self._section_lines("Benefits", data["sections"].get("benefits", []), limit=2))
            lines.extend(self._section_lines("Documents", data["sections"].get("required_documents", []), limit=2))
            lines.extend(self._section_lines("How to apply", data["sections"].get("application_process", []), limit=2))
            if data.get("source_url"):
                lines.append(f"Source: {data['source_url']}")
            lines.append("")

        lines.append("I only used scraped/indexed scheme evidence. Please verify final eligibility on the official source before applying.")
        return "\n".join(lines).strip()

    def _section_lines(self, title: str, values: list[str], limit: int) -> list[str]:
        clean_values = [self._compact(value) for value in values if value]
        if not clean_values:
            return []
        lines = [f"{title}:"]
        for value in clean_values[:limit]:
            lines.append(f"- {value}")
        return lines

    def _compact(self, text: str, max_length: int = 450) -> str:
        text = " ".join(text.split())
        if len(text) <= max_length:
            return text
        return text[: max_length - 3].rsplit(" ", 1)[0] + "..."

    def _confidence_label(self, score: float) -> str:
        if score >= 0.70:
            return "strong match"
        if score >= 0.50:
            return "good match"
        return "possible match"

    def _sources(self, results: list[dict[str, Any]]) -> list[str]:
        return sorted({str(item["source_url"]) for item in results if item.get("source_url")})

    def _join_warnings(self, first: str | None, second: str | None) -> str | None:
        warnings = [warning for warning in [first, second] if warning]
        return " ".join(warnings) if warnings else None
