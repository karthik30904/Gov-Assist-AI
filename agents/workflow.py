from __future__ import annotations

from langgraph.graph import END, StateGraph

from .action_plan_agent import action_plan_agent
from .eligibility_reasoning_agent import eligibility_reasoning_agent
from .grounding_agent import grounding_agent
from .hybrid_retrieval_agent import hybrid_retrieval_agent
from .intent_agent import intent_agent
from .profile_agent import profile_agent
from .research_planner_agent import research_planner_agent
from .state import AgentState
from .web_research_agent import web_research_agent


def build_research_graph():
    graph = StateGraph(AgentState)
    graph.add_node("profile", profile_agent)
    graph.add_node("intent", intent_agent)
    graph.add_node("research_planner", research_planner_agent)
    graph.add_node("web_research", web_research_agent)
    graph.add_node("hybrid_retrieval", hybrid_retrieval_agent)
    graph.add_node("eligibility_reasoning", eligibility_reasoning_agent)
    graph.add_node("action_plan", action_plan_agent)
    graph.add_node("grounding", grounding_agent)

    graph.set_entry_point("profile")
    graph.add_edge("profile", "intent")
    graph.add_edge("intent", "research_planner")
    graph.add_conditional_edges(
        "research_planner",
        lambda state: "web_research" if state.get("needs_more_research") else "hybrid_retrieval",
        {"web_research": "web_research", "hybrid_retrieval": "hybrid_retrieval"},
    )
    graph.add_edge("web_research", "hybrid_retrieval")
    graph.add_edge("hybrid_retrieval", "eligibility_reasoning")
    graph.add_edge("eligibility_reasoning", "action_plan")
    graph.add_edge("action_plan", "grounding")
    graph.add_edge("grounding", END)
    return graph.compile()
