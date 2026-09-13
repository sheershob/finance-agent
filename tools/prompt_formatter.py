"""
Formatting utilities to convert structured analysis objects (DebtAnalysis,
GoalAnalysis, expense breakdowns) into human-readable, LLM-friendly prompt text.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.debt import DebtAnalysis
    from schemas.goal import GoalAnalysis
    from schemas.common import CategoryAmount


def format_debt_analysis_for_prompt(debt_analysis: list[DebtAnalysis] | None) -> str:
    """
    Format DebtAnalysis objects into clean, structured prompt text.
    """
    if not debt_analysis:
        return "No active debt data available."

    formatted_items = []
    for item in debt_analysis:
        d = item.debt
        line = (
            f"• {d.loan_name} — Principal: ₹{d.outstanding_principal:,.2f} @ {d.interest_rate}% p.a. | "
            f"EMI: ₹{d.monthly_emi:,.2f}/mo | Tenure: {d.remaining_tenure_months} months\n"
            f"  - Total Remaining Repayment: ₹{item.total_remaining_payment:,.2f}\n"
            f"  - Estimated Remaining Interest: ₹{item.estimated_remaining_interest:,.2f}\n"
            f"  - Monthly Principal Component: ₹{item.monthly_principal_component:,.2f}\n"
            f"  - Monthly Interest Component: ₹{item.monthly_interest_component:,.2f}\n"
            f"  - Interest-to-Principal Ratio: {item.interest_to_principal_ratio}%"
        )
        if item.is_insufficient and item.warning_message:
            line += f"\n  - ⚠️ WARNING: {item.warning_message}"
        if item.prepayment_savings > 0:
            line += (
                f"\n  - Potential Prepayment Savings: ₹{item.prepayment_savings:,.2f} "
                f"({item.prepayment_months_saved} months saved)"
            )
        formatted_items.append(line)

    return "\n\n".join(formatted_items)


def format_goal_analysis_for_prompt(goal_analysis: list[GoalAnalysis] | None) -> str:
    """
    Format GoalAnalysis objects into clean, structured prompt text.
    """
    if not goal_analysis:
        return "No active goal data available."

    formatted_items = []
    for item in goal_analysis:
        g = item.goal
        category_str = f" | Category: {g.category}" if g.category else ""
        priority_str = f" | Priority: {g.priority}/5" if g.priority else ""

        line = (
            f"• {g.name} — Target: ₹{g.target_amount:,.2f} | Current Savings: ₹{g.current_amount:,.2f} "
            f"({item.progress_percentage:.1f}% reached){category_str}{priority_str}\n"
            f"  - Target Time Horizon: {g.time_horizon_months} months\n"
            f"  - Required Monthly Saving: ₹{item.required_monthly_saving:,.2f}/mo\n"
            f"  - Monthly Funding Gap: ₹{item.funding_gap:,.2f}\n"
            f"  - Goal Feasibility: {'✅ Feasible' if item.is_feasible else '⚠️ Infeasible (required monthly saving exceeds available surplus)'}"
        )
        formatted_items.append(line)

    return "\n\n".join(formatted_items)


def format_categories_for_prompt(categories: list[CategoryAmount] | dict | None) -> str:
    """
    Format expense breakdowns or top categories into clean text.
    """
    if not categories:
        return "None available."

    if isinstance(categories, list):
        lines = [
            f"• {getattr(item.category, 'value', str(item.category))}: ₹{item.amount:,.2f}"
            for item in categories
        ]
        return "\n".join(lines)

    if isinstance(categories, dict):
        lines = [f"• {k}: ₹{v:,.2f}" for k, v in categories.items()]
        return "\n".join(lines)

    return str(categories)
