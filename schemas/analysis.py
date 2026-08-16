"""
This represents the results of the financial analysis.
"""
from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field

from schemas.common import CategoryAmount
from schemas.budget import MonthlyBudget
from schemas.goal import GoalAnalysis
from schemas.debt import DebtAnalysis


class FinancialAnalysis(BaseModel):

    # Expense Analysis
    monthly_income: Decimal
    monthly_expenses: Decimal
    monthly_surplus: Decimal
    savings_rate: Decimal

    expense_breakdown: list[CategoryAmount]
    top_categories: list[CategoryAmount]

    # Budget
    budget: MonthlyBudget

    # Goals
    goal_analysis: list[GoalAnalysis]

    # Debts
    debt_analysis: list[DebtAnalysis]

    # Health Metrics
    debt_to_income_ratio: Decimal
    emergency_fund_months: Decimal

    # Overall
    financial_health_score: int = Field(
        ge=0,
        le=100,
    )