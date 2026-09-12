"""
Prompt template for the Report Agent.
"""

from __future__ import annotations

from schemas.analysis import FinancialAnalysis
from tools.prompt_formatter import (
    format_debt_analysis_for_prompt,
    format_goal_analysis_for_prompt,
    format_categories_for_prompt,
)


def build_report_prompt(
    analysis: FinancialAnalysis,
) -> str:
    debt_str = format_debt_analysis_for_prompt(analysis.debt_analysis)
    goal_str = format_goal_analysis_for_prompt(analysis.goal_analysis)
    breakdown_str = format_categories_for_prompt(analysis.expense_breakdown)
    top_cats_str = format_categories_for_prompt(analysis.top_categories)

    return f"""
You are an expert Financial Report Writer.

Generate a professional financial report.

The report should be written in markdown.

Do NOT invent numbers.

Use only the provided data.

Do NOT include any calendar dates, date estimates, or date references in the report.
Ignore date values present in the supplied goal or debt analysis. If timing is
necessary, express it only as a relative duration in months.

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

Goal Analysis

{goal_str}

Debt Analysis

{debt_str}

Expense Breakdown

{breakdown_str}

Top Spending Categories

{top_cats_str}

Generate a markdown report using the following sections.

# Overall Summary

# Financial Overview

# Income and Expenses

# Budget Analysis

# Financial Health

# Key Recommendations

# Next Steps

Use tables where appropriate.

Keep the report between 700 and 1200 words.

The report should sound professional and suitable for a financial advisor.
Do not include dates.
""".strip()
