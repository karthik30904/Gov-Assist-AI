from __future__ import annotations

from .state import AgentState


def eligibility_reasoning_agent(state: AgentState) -> AgentState:
    results = state.get("retrieval_results", [])
    profile = state.get("citizen_profile", {})
    eligibility_text = " ".join(item.get("text", "") for item in results if item.get("section") == "eligibility").lower()

    if not eligibility_text:
        state["eligibility_status"] = "Partially Eligible"
    elif all(str(value).lower() in eligibility_text for value in profile.values() if isinstance(value, str)):
        state["eligibility_status"] = "Eligible"
    elif profile:
        state["eligibility_status"] = "Partially Eligible"
    else:
        state["eligibility_status"] = "Partially Eligible"
    return state
