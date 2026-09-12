"""
Prompt template for the Recommendation Agent.
"""

from __future__ import annotations

from schemas.analysis import FinancialAnalysis
from tools.prompt_formatter import (
    format_debt_analysis_for_prompt,
    format_goal_analysis_for_prompt,
    format_categories_for_prompt,
)


def build_recommendation_prompt(
    analysis: FinancialAnalysis,
) -> str:
    debt_str = format_debt_analysis_for_prompt(analysis.debt_analysis)
    goal_str = format_goal_analysis_for_prompt(analysis.goal_analysis)
    breakdown_str = format_categories_for_prompt(analysis.expense_breakdown)
    top_cats_str = format_categories_for_prompt(analysis.top_categories)

    return f"""
You are an expert AI Financial Advisor.

Your task is to analyze the user's financial situation and generate personalized recommendations.

The recommendations must be:
- Practical
- Actionable
- Easy to understand
- Prioritized
- Personalized

Do NOT invent financial information.

Do NOT change any of the numerical values.

Do NOT include any calendar dates, date estimates, or date references in your response.
If timing is necessary, express it only as a relative duration in months.

Financial Summary

Monthly Income:
₹{analysis.monthly_income:,.2f}

Monthly Expenses:
₹{analysis.monthly_expenses:,.2f}

Monthly Surplus:
₹{analysis.monthly_surplus:,.2f}

Savings Rate:
{analysis.savings_rate}%

Debt-to-Income Ratio:
{analysis.debt_to_income_ratio}%

Emergency Fund:
{analysis.emergency_fund_months} months

Financial Health Score:
{analysis.financial_health_score}/100

Budget

{analysis.budget.to_prompt_string()}

Debt Analysis

{debt_str}

Goal Analysis

{goal_str}

Expense Breakdown

{breakdown_str}

Top Spending Categories

{top_cats_str}

Generate between 6 and 10 recommendations.

Recommendations should focus on:

1. Expense reduction
2. Savings improvement
3. Investment opportunities
4. Debt reduction
5. Emergency fund
6. Goal planning
7. Budget optimization

Return ONLY bullet points.

Do not use markdown headings.

Do not repeat the financial summary.
Do not include dates.
""".strip()
