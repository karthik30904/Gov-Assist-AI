from __future__ import annotations

from .state import AgentState


def action_plan_agent(state: AgentState) -> AgentState:
    results = state.get("retrieval_results", [])
    sources = sorted({item.get("source_url", "") for item in results if item.get("source_url")})
    documents = [item["text"] for item in results if item.get("section") == "required_documents"]
    application = [item["text"] for item in results if item.get("section") == "application_process"]

    state["sources"] = sources
    state["answer"] = "\n".join(
        [
            f"Eligibility: {state.get('eligibility_status', 'Partially Eligible')}",
            "Recommended actions:",
            *(application or ["Review the source scheme page and confirm the latest application route."]),
            "Required documents:",
            *(documents or ["Documents were not found in the retrieved evidence. Trigger fresh research."]),
        ]
    )
    return state
