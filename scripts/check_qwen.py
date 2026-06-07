from __future__ import annotations

import asyncio

from llm import QwenClient


async def main() -> None:
    client = QwenClient(model="qwen2.5:14b")
    result = await client.generate_grounded_answer(
        query="Check whether Qwen is working.",
        evidence=[
            {
                "scheme_name": "Connectivity Test Scheme",
                "section": "overview",
                "score": 1.0,
                "source_url": "local-test",
                "text": "This is a local test evidence chunk used only to verify model generation.",
                "metadata": {},
            }
        ],
    )
    if result.error:
        raise SystemExit(f"Qwen check failed: {result.error}")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
