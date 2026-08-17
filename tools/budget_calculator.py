"""
Generates a recommended monthly budget from calculated spending metrics.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from schemas.budget import (
    BudgetAllocation,
    MonthlyBudget,
)
from schemas.common import CategoryAmount
from schemas.enums import ExpenseCategory


class BudgetCalculator:
    """
    Generates a recommended monthly budget.
    """

    DEFAULT_INVESTMENT_RATIO = Decimal("0.60")
    DEFAULT_EMERGENCY_RATIO = Decimal("0.20")

    def generate_budget(
        self,
        monthly_income: Decimal,
        monthly_surplus: Decimal,
        expense_breakdown: list[CategoryAmount],
    ) -> MonthlyBudget:
        """Generate a budget from the expense summary produced by ExpenseCalculator."""

        allocations = self._calculate_allocations(
            expense_breakdown
        )

        expected_savings = max(monthly_surplus, Decimal("0"))

        recommended_investment = (
            self._calculate_recommended_investment(
                expected_savings
            )
        )

        emergency_fund = (
            self._calculate_emergency_fund_contribution(
                expected_savings
            )
        )

        remaining_balance = (
            self._calculate_remaining_balance(
                expected_savings,
                recommended_investment,
                emergency_fund,
            )
        )

        total_budget = sum(
            (allocation.recommended_amount for allocation in allocations),
            Decimal("0"),
        )

        return MonthlyBudget(
            monthly_income=monthly_income,
            total_budget=total_budget,
            allocations=allocations,
            expected_savings=expected_savings,
            recommended_investment=recommended_investment,
            emergency_fund_contribution=emergency_fund,
            remaining_balance=remaining_balance,
        )

    def _calculate_allocations(
        self,
        breakdown: list[CategoryAmount],
    ) -> list[BudgetAllocation]:
        """
        Generate recommended allocations based on
        historical spending.

        Strategy:
        - Keep essential expenses unchanged.
        - Reduce discretionary expenses by 10%.
        """

        allocations = []

        discretionary_categories = {
            ExpenseCategory.SHOPPING,
            ExpenseCategory.ENTERTAINMENT,
            ExpenseCategory.TRAVEL,
        }

        for item in breakdown:

            category = ExpenseCategory(item.category)

            amount = item.amount

            if category in discretionary_categories:
                amount *= Decimal("0.90")

            allocations.append(
                BudgetAllocation(
                    category=category,
                    recommended_amount=self._round(amount),
                )
            )

        return allocations

    def _calculate_recommended_investment(self,savings: Decimal) -> Decimal:

        if savings <= 0:
            return Decimal("0")

        investment = (
            savings
            * self.DEFAULT_INVESTMENT_RATIO
        )

        return self._round(investment)

    def _calculate_emergency_fund_contribution(self,savings: Decimal) -> Decimal:

        if savings <= 0:
            return Decimal("0")

        contribution = (
            savings
            * self.DEFAULT_EMERGENCY_RATIO
        )

        return self._round(contribution)

    def _calculate_remaining_balance(self,savings: Decimal,investment: Decimal,emergency: Decimal) -> Decimal:

        remaining = (
            savings
            - investment
            - emergency
        )

        if remaining < 0:
            return Decimal("0")

        return self._round(remaining)
    def _round(self, value: Decimal) -> Decimal:
        """
        Round monetary values to two decimal places.
        """

        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

    def budget_summary(self,budget: MonthlyBudget) -> str:
        """
        Generate a human-readable budget summary.

        Useful for:
        - Streamlit UI
        - Logs
        - Report Agent
        """

        lines = [
            "========== Monthly Budget ==========",
            f"Monthly Income               : ₹{budget.monthly_income}",
            f"Total Budget                 : ₹{budget.total_budget}",
            "",
            "Category Allocations:",
        ]

        for allocation in budget.allocations:
            lines.append(
                f"  • {allocation.category.value:<18} ₹{allocation.recommended_amount}"
            )

        lines.extend(
            [
                "",
                f"Expected Savings            : ₹{budget.expected_savings}",
                f"Recommended Investment      : ₹{budget.recommended_investment}",
                f"Emergency Fund Contribution : ₹{budget.emergency_fund_contribution}",
                f"Remaining Balance           : ₹{budget.remaining_balance}",
                "====================================",
            ]
        )

        return "\n".join(lines)

    def budget_as_dict(self,budget: MonthlyBudget) -> dict:
        """
        Convert the MonthlyBudget schema into
        a dictionary.

        Useful when exporting to JSON,
        dashboards, or reports.
        """

        return {
            "monthly_income": budget.monthly_income,
            "total_budget": budget.total_budget,
            "allocations": {
                allocation.category.value: allocation.recommended_amount
                for allocation in budget.allocations
            },
            "expected_savings": budget.expected_savings,
            "recommended_investment": budget.recommended_investment,
            "emergency_fund_contribution": budget.emergency_fund_contribution,
            "remaining_balance": budget.remaining_balance,
        }
