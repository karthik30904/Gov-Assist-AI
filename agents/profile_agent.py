from __future__ import annotations

import re

from .state import AgentState


def profile_agent(state: AgentState) -> AgentState:
    query = state.get("query", "")
    profile = dict(state.get("citizen_profile", {}))

    age_match = re.search(r"\b(\d{1,3})\s*(?:years?|yrs?)\b", query, re.I)
    if age_match:
        profile["age"] = int(age_match.group(1))

    for marker in ["student", "farmer", "woman", "senior citizen", "disabled", "entrepreneur"]:
        if marker in query.lower():
            profile.setdefault("traits", []).append(marker)

    state["citizen_profile"] = profile
    return state
