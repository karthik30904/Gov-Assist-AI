from __future__ import annotations

from typing import Any, TypedDict

from models import Scheme, SchemeChunk


class AgentState(TypedDict, total=False):
    query: str
    citizen_profile: dict[str, Any]
    intent: str
    research_decision: str
    schemes: list[Scheme]
    chunks: list[SchemeChunk]
    retrieval_results: list[dict[str, Any]]
    eligibility_status: str
    answer: str
    sources: list[str]
    needs_more_research: bool
