from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import aiohttp


@dataclass
class LlmResult:
    text: str | None
    model: str
    error: str | None = None


class QwenClient:
    def __init__(
        self,
        model: str | None = None,
        base_url: str | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        self.model = model or os.getenv("QWEN_MODEL", "qwen2.5:14b")
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.timeout_seconds = timeout_seconds

    async def generate_grounded_answer(self, query: str, evidence: list[dict[str, Any]]) -> LlmResult:
        if not evidence:
            return LlmResult(text=None, model=self.model, error="No retrieved evidence was provided.")

        prompt = self._build_prompt(query, evidence)
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are Gov Assist AI, a careful Indian government scheme assistant. "
                        "Answer only from the supplied myScheme evidence. Be clear, useful, and specific. "
                        "If evidence is incomplete, say what is missing. Always include source labels like [S1]."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "options": {
                "temperature": 0.15,
                "top_p": 0.9,
                "num_ctx": 8192,
            },
        }

        timeout = aiohttp.ClientTimeout(total=self.timeout_seconds)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{self.base_url}/api/chat", json=payload) as response:
                    if response.status >= 400:
                        body = await response.text()
                        return LlmResult(
                            text=None,
                            model=self.model,
                            error=f"Ollama returned HTTP {response.status}: {body[:300]}",
                        )
                    data = await response.json()
        except TimeoutError:
            return LlmResult(text=None, model=self.model, error="Qwen generation timed out.")
        except aiohttp.ClientError as exc:
            return LlmResult(text=None, model=self.model, error=f"Could not reach Ollama: {exc}")

        message = data.get("message", {})
        text = message.get("content")
        if not text:
            return LlmResult(text=None, model=self.model, error="Ollama returned an empty response.")
        return LlmResult(text=text.strip(), model=self.model)

    def _build_prompt(self, query: str, evidence: list[dict[str, Any]]) -> str:
        evidence_blocks = []
        for index, item in enumerate(evidence[:10], start=1):
            metadata = item.get("metadata", {})
            evidence_blocks.append(
                "\n".join(
                    [
                        f"[S{index}]",
                        f"Scheme: {item.get('scheme_name') or metadata.get('scheme_name') or 'Unknown'}",
                        f"Section: {item.get('section') or metadata.get('section') or 'evidence'}",
                        f"Score: {float(item.get('score', 0.0)):.3f}",
                        f"Source URL: {item.get('source_url') or metadata.get('source_url') or 'not available'}",
                        f"Evidence: {item.get('text', '')}",
                    ]
                )
            )

        return (
            f"User question:\n{query}\n\n"
            "Retrieved myScheme evidence:\n"
            + "\n\n".join(evidence_blocks)
            + "\n\nWrite the final answer with these sections:\n"
            "1. Short answer\n"
            "2. Best matching scheme(s)\n"
            "3. Eligibility reasoning\n"
            "4. Benefits\n"
            "5. Required documents\n"
            "6. Application steps\n"
            "7. Sources\n\n"
            "Rules: do not invent eligibility, benefits, documents, dates, or links. "
            "Use the source labels in every factual bullet."
        )
