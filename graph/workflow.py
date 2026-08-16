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
)


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

    graph.add_edge(
        START,
        "analyze_finances",
    )

    graph.add_edge(
        "analyze_finances",
        "generate_recommendations",
    )

    graph.add_edge(
        "generate_recommendations",
        "generate_report",
    )

    graph.add_edge(
        "generate_report",
        END,
    )

    return graph.compile()