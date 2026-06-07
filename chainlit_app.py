from __future__ import annotations

import chainlit as cl

from services import SchemeRagService


@cl.on_chat_start
async def on_chat_start() -> None:
    await cl.Message(
        content=(
            "Gov Assist AI is ready. I will answer from scraped myScheme evidence, "
            "index fresh pages into ChromaDB when needed, and show sources."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    status = cl.Message(
        content=(
            "Searching ChromaDB, refreshing myScheme evidence if needed, "
            "then generating with qwen2.5:14b..."
        )
    )
    await status.send()

    try:
        service = cl.user_session.get("rag_service")
        if service is None:
            service = SchemeRagService()
            cl.user_session.set("rag_service", service)
        result = await service.answer(message.content)
    except Exception as exc:
        await cl.Message(
            content=(
                "I hit an application error before generating the answer.\n\n"
                f"Error: `{type(exc).__name__}: {exc}`\n\n"
                "Please paste the terminal logs and I will fix the exact failing part."
            )
        ).send()
        return

    answer = result.answer
    if result.warning:
        answer += f"\n\nWarning: {result.warning}"
    if result.crawled:
        answer += f"\n\nFresh crawl: indexed {result.crawled} scheme page(s)."
    answer += (
        f"\n\nModel: {result.model_used}"
        f"\nLLM generated: {'yes' if result.llm_used else 'no, used evidence fallback'}"
        f"\nRetrieved evidence chunks: {result.retrieved}"
    )

    await cl.Message(content=answer).send()
