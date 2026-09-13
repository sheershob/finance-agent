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
        """Return a human-readable budget summary for the prompt."""
        lines = [
            "Total Budget:",
            f"₹{self.total_budget}",
            "",
            "Category Allocations:",
        ]

        if self.allocations:
            for allocation in self.allocations:
                lines.append(
                    f"{allocation.category.value}: ₹{allocation.recommended_amount}"
                )
        else:
            lines.append("No allocation data available.")

        lines.extend(
            [
                "",
                "Expected Savings:",
                f"₹{self.expected_savings}",
                "",
                "Recommended Investment:",
                f"₹{self.recommended_investment}",
                "",
                "Emergency Fund Contribution:",
                f"₹{self.emergency_fund_contribution}",
                "",
                "Remaining Balance:",
                f"₹{self.remaining_balance}",
            ]
        )

        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_prompt_string()
