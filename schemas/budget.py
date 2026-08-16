from __future__ import annotations
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from .enums import ExpenseCategory


class BudgetAllocation(BaseModel):
    """
    Budget for a single category.
    """

    category: ExpenseCategory

    recommended_amount: float = Field(
        ge=0
    )

class MonthlyBudget(BaseModel):
    """
    Represents the complete monthly budget plan.
    """

    monthly_income: Decimal = Field(
        ge=0,
        description="Monthly income used to generate the budget."
    )

    total_budget: Decimal = Field(
        ge=0,
        description="Total planned spending budget."
    )

    allocations: list[BudgetAllocation] = Field(
        default_factory=list
    )

    expected_savings: Decimal = Field(
        ge=0,
        description="Expected monthly savings."
    )

    recommended_investment: Decimal = Field(
        ge=0,
        description="Recommended monthly investment amount."
    )

    emergency_fund_contribution: Decimal = Field(
        ge=0,
        description="Suggested monthly emergency fund contribution."
    )

    remaining_balance: Decimal = Field(
        ge=0,
        description="Unallocated money remaining after budgeting."
    )