from __future__ import annotations

import chainlit as cl

from services import SchemeRagService


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("rag_service", SchemeRagService())
    await cl.Message(
        content=(
            "Gov Assist AI is ready. I will answer from scraped myScheme evidence, "
            "index fresh pages into ChromaDB when needed, and show sources."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    service = cl.user_session.get("rag_service") or SchemeRagService()
    status = cl.Message(content="Searching ChromaDB and refreshing from myScheme if evidence is weak...")
    await status.send()

    result = await service.answer(message.content)
    answer = result.answer
    if result.crawled:
        answer += f"\n\nFresh crawl: indexed {result.crawled} scheme page(s)."
    answer += f"\nRetrieved evidence chunks: {result.retrieved}"

    await cl.Message(content=answer).send()
