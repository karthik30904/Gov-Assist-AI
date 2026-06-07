from __future__ import annotations

from .state import AgentState


def grounding_agent(state: AgentState) -> AgentState:
    answer = state.get("answer", "")
    sources = state.get("sources", [])
    if not sources:
        state["answer"] = answer + "\n\nGrounding warning: no source URL was retrieved."
    return state
