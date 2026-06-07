from __future__ import annotations

from retrieval.hybrid_retriever import HybridRetriever

from .state import AgentState


def research_planner_agent(state: AgentState, retriever: HybridRetriever | None = None) -> AgentState:
    if retriever is None or not retriever.chunks:
        state["research_decision"] = "fresh_crawl"
        state["needs_more_research"] = True
        return state

    results = retriever.search(state.get("query", ""), top_k=3)
    if retriever.quality_sufficient(results):
        state["research_decision"] = "use_existing_knowledge"
        state["needs_more_research"] = False
        state["retrieval_results"] = [
            {"text": result.chunk.text, "score": result.score, "source_url": str(result.chunk.source_url)}
            for result in results
        ]
    else:
        state["research_decision"] = "fresh_crawl"
        state["needs_more_research"] = True
    return state
