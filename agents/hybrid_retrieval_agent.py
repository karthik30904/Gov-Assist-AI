from __future__ import annotations

from retrieval.hybrid_retriever import HybridRetriever

from .state import AgentState


def hybrid_retrieval_agent(state: AgentState, retriever: HybridRetriever | None = None) -> AgentState:
    if retriever is None:
        retriever = HybridRetriever(state.get("chunks", []))
    results = retriever.search(state.get("query", ""), top_k=5)
    state["retrieval_results"] = [
        {
            "scheme_name": result.chunk.scheme_name,
            "text": result.chunk.text,
            "section": result.chunk.section,
            "score": result.score,
            "source_url": str(result.chunk.source_url),
        }
        for result in results
    ]
    state["needs_more_research"] = not retriever.quality_sufficient(results)
    return state
