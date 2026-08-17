"""
LangGraph node functions for the financial-planning workflow.

Each node receives the current FinancialState and returns
the state updates produced by that node.
"""

from __future__ import annotations
from decimal import Decimal
from tools.financial_analyzer import FinancialAnalyzer
from graph.state import FinancialState
from agents.recommendation_agent import RecommendationAgent
from agents.report_agent import ReportAgent
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


financial_analyzer = FinancialAnalyzer()
recommendation_agent = RecommendationAgent()
report_agent = ReportAgent()

def analyze_finances(state: FinancialState) -> FinancialState:
    """
    Run deterministic financial analysis.
    """

    logger.info("START: analyze_finances")
    try:
        batch = state["transactions"]
        transaction_count = len(batch.transactions) if hasattr(batch, "transactions") else 0

        logger.info(
            "Transactions received: %d",
            transaction_count,
        )

        analysis = financial_analyzer.analyze(
            transactions=batch,
            goals=state.get("goals", []),
            debts=state.get("debts", []),
            emergency_fund=state.get(
                "emergency_fund",
                Decimal("0"),
            ),
        )

        logger.info("END: analyze_finances")

        return {
            **state,
            "financial_analysis": analysis,
            "budget": analysis.budget,
            "goal_analysis": analysis.goal_analysis,
            "debt_analysis": analysis.debt_analysis,
            "current_step": "financial_analysis",
        }

    except Exception as exc:

        logger.exception(
            "ERROR: analyze_finances"
        )

        return {
            **state,
            "errors": [
                *state.get("errors", []),
                f"Financial analysis failed: {exc}",
            ],
            "current_step": "financial_analysis_failed",
        }
    
def generate_recommendations(state: FinancialState) -> FinancialState:

    logger.info("START: generate_recommendations")

    if "financial_analysis" not in state:
        logger.warning(
            "Skipping recommendations: financial_analysis missing from state."
        )
        return {
            **state,
            "current_step": "recommendations_skipped",
        }

    recommendations = recommendation_agent.generate(
        state["financial_analysis"]
    )

    logger.info("END: generate_recommendations")

    return {
        **state,
        "recommendations": recommendations,
        "current_step": "recommendations",
    }

def generate_report(state: FinancialState) -> FinancialState:
    logger.info("START: generate_report")

    if "financial_analysis" not in state:
        logger.warning(
            "Skipping report generation: financial_analysis missing from state."
        )
        return {
            **state,
            "current_step": "report_skipped",
        }

    report = report_agent.generate(
        state["financial_analysis"]
    )

    logger.info("END: generate_report")

    return {
        **state,
        "report": report,
        "current_step": "report",
    }

def handle_error(state: FinancialState) -> FinancialState:
    """
    Final error-handling node.

    Keeps the workflow from crashing when a previous node
    records an error.
    """

    return {
        **state,
        "current_step": "error",
    }