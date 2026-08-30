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

    recommended_amount: Decimal = Field(
        ge=0
    )

    def to_prompt_string(self) -> str:
        """Return a compact, LLM-safe representation."""
        return (
            f"category={self.category.value}, "
            f"recommended_amount={self.recommended_amount}"
        )

    def __str__(self) -> str:
        return self.to_prompt_string()


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

    def to_prompt_string(self) -> str:
        """Return a compact, LLM-safe budget summary."""
        allocations = ", ".join(
            str(allocation) for allocation in self.allocations
        )
        return (
            "monthly_income=" + str(self.monthly_income)
            + " total_budget=" + str(self.total_budget)
            + f" allocations=[{allocations}]"
            + " expected_savings=" + str(self.expected_savings)
            + " recommended_investment=" + str(self.recommended_investment)
            + " emergency_fund_contribution=" + str(self.emergency_fund_contribution)
            + " remaining_balance=" + str(self.remaining_balance)
        )

    def __str__(self) -> str:
        return self.to_prompt_string()
