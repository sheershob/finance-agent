"""
Defines the LangGraph workflow for the financial-planning
application.
"""
from langgraph.graph import StateGraph, START, END

from graph.state import FinancialState
from graph.nodes import (
    analyze_finances,
    generate_recommendations,
    generate_report,
    handle_error,
)


def route_after_analysis(state: FinancialState) -> str:
    """
    Stop the workflow when financial analysis fails; otherwise continue.
    """
    if state.get("current_step") == "financial_analysis_failed":
        return "handle_error"
    return "generate_recommendations"


def build_workflow():
    """
    Build and compile the financial-planning LangGraph.
    """

    graph = StateGraph(FinancialState)

    graph.add_node(
        "analyze_finances",
        analyze_finances,
    )

    graph.add_node(
        "generate_recommendations",
        generate_recommendations,
    )

    graph.add_node(
        "generate_report",
        generate_report,
    )

    graph.add_node(
        "handle_error",
        handle_error,
    )

    graph.add_edge(
        START,
        "analyze_finances",
    )

    graph.add_conditional_edges(
        "analyze_finances",
        route_after_analysis,
    )

    graph.add_edge(
        "generate_recommendations",
        "generate_report",
    )

    graph.add_edge(
        "generate_report",
        END,
    )

    graph.add_edge(
        "handle_error",
        END,
    )

    return graph.compile()