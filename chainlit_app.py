from __future__ import annotations

import chainlit as cl

from agents.workflow import build_research_graph


@cl.on_chat_start
async def on_chat_start() -> None:
    cl.user_session.set("graph", build_research_graph())
    await cl.Message(
        content=(
            "Gov Assist AI is ready. Ask about Indian government schemes, eligibility, "
            "required documents, or application steps."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message) -> None:
    graph = cl.user_session.get("graph") or build_research_graph()
    result = await graph.ainvoke({"query": message.content})

    answer = result.get("answer") or "I could not produce a grounded answer from the available evidence."
    sources = result.get("sources") or []
    if sources:
        answer += "\n\nSources:\n" + "\n".join(f"- {source}" for source in sources)

    await cl.Message(content=answer).send()
