from __future__ import annotations

from crawler import MySchemeCrawler
from retrieval.chunking import chunk_scheme

from .state import AgentState


async def web_research_agent(state: AgentState, crawler: MySchemeCrawler | None = None) -> AgentState:
    crawler = crawler or MySchemeCrawler()
    schemes = await crawler.crawl(query=state.get("query"), limit=25)
    chunks = [chunk for scheme in schemes for chunk in chunk_scheme(scheme)]
    state["schemes"] = schemes
    state["chunks"] = chunks
    state["needs_more_research"] = False
    return state
