import os
import time
from typing import TypedDict

from langgraph.graph import StateGraph, END
from langgraph.errors import GraphRecursionError

from .agents import planner, researcher, writer, critic
from .llm import BudgetExceeded


MAX_REVISIONS = int(os.getenv("MAX_REVISIONS", "2"))


class ResearchState(TypedDict, total=False):
    topic: str
    questions: list
    findings: list
    draft: str
    feedback: str
    score: int
    revisions: int
    tokens_used: int
    trace: list


# Decide whether to revise or finish
def route_after_critic(state):

    if state["score"] >= 7:
        return "done"

    if state["revisions"] > MAX_REVISIONS:
        return "done"

    return "revise"


# Connect all four agents
def build_graph():

    graph = StateGraph(ResearchState)

    graph.add_node("planner", planner)
    graph.add_node("researcher", researcher)
    graph.add_node("writer", writer)
    graph.add_node("critic", critic)

    graph.set_entry_point("planner")

    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "critic")

    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {
            "revise": "writer",
            "done": END
        }
    )

    return graph.compile()


# Create the workflow
graph = build_graph()


# Run research
def run_research(topic):

    state = {
        "topic": topic,
        "revisions": 0,
        "tokens_used": 0,
        "trace": [],
        "feedback": "",
        "draft": "",
        "score": 0
    }

    start = time.time()

    try:

        final = graph.invoke(
            state,
            config={"recursion_limit": 15}
        )

        status = "ok"

    except (
        BudgetExceeded,
        GraphRecursionError,
        RuntimeError
    ) as error:

        status = "needs_human"
        final = state

        final["trace"].append(
            f"STOPPED: {error}"
        )

    return {
        "status": status,
        "report": final.get("draft", ""),
        "score": final.get("score", 0),
        "revisions": final.get("revisions", 0),
        "tokens_used": final.get("tokens_used", 0),
        "seconds": round(time.time() - start, 1),
        "trace": final.get("trace", [])
    }
