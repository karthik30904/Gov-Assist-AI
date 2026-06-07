from __future__ import annotations

from .state import AgentState


def intent_agent(state: AgentState) -> AgentState:
    query = state.get("query", "").lower()
    if "eligible" in query or "eligibility" in query:
        state["intent"] = "eligibility_check"
    elif "apply" in query or "documents" in query:
        state["intent"] = "application_guidance"
    else:
        state["intent"] = "scheme_discovery"
    return state
