"""
report_prompt.py

Prompt template for the Report Agent.
"""

from __future__ import annotations

from schemas.analysis import FinancialAnalysis


def build_report_prompt(
    analysis: FinancialAnalysis,
) -> str:

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
₹{analysis.monthly_income}

Monthly Expenses:
₹{analysis.monthly_expenses}

Monthly Surplus:
₹{analysis.monthly_surplus}

Savings Rate:
{analysis.savings_rate}%

Debt-to-Income Ratio:
{analysis.debt_to_income_ratio}%

Emergency Fund:
{analysis.emergency_fund_months} months

Financial Health Score:
{analysis.financial_health_score}/100

Budget

{analysis.budget}

Goal Analysis

{analysis.goal_analysis}

Debt Analysis

{analysis.debt_analysis}

Expense Breakdown

{analysis.expense_breakdown}

Top Spending Categories

{analysis.top_categories}

Generate a markdown report using the following sections.

# Executive Summary

# Financial Overview

# Income and Expenses

# Budget Analysis

# Debt Analysis

# Goal Analysis

# Financial Health

# Key Recommendations

# Next Steps

Use tables where appropriate.

Keep the report between 700 and 1200 words.

The report should sound professional and suitable for a financial advisor.
Do not include dates.
""".strip()
