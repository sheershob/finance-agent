"""
Combines the outputs of the deterministic financial calculators
into a single FinancialAnalysis object.

This module contains no LLM logic and makes no financial
recommendations. Its job is to aggregate and derive
high-level financial metrics.
"""
from __future__ import annotations

from decimal import Decimal

from schemas.transaction import TransactionBatch
from schemas.analysis import FinancialAnalysis
from schemas.debt import Debt
from schemas.enums import ExpenseCategory, TransactionType
from schemas.goal import FinancialGoal, GoalAnalysis

from tools.expense_calculator import ExpenseCalculator
from tools.budget_calculator import BudgetCalculator
from tools.goal_calculator import GoalCalculator
from tools.debt_calculator import DebtCalculator


class FinancialAnalyzer:
    """
    Coordinates the deterministic financial calculators and
    produces a complete FinancialAnalysis.
    """

    def __init__(
        self,
        expense_calculator: ExpenseCalculator | None = None,
        budget_calculator: BudgetCalculator | None = None,
        goal_calculator: GoalCalculator | None = None,
        debt_calculator: DebtCalculator | None = None,
    ) -> None:

        self.expense_calculator = (
            expense_calculator or ExpenseCalculator()
        )

        self.budget_calculator = (
            budget_calculator or BudgetCalculator()
        )

        self.goal_calculator = (
            goal_calculator or GoalCalculator()
        )

        self.debt_calculator = (
            debt_calculator or DebtCalculator()
        )

    def analyze(
        self,
        transactions: TransactionBatch,
        goals: list[FinancialGoal] | None = None,
        debts: list[Debt] | None = None,
        emergency_fund: Decimal = Decimal("0"),
    ) -> FinancialAnalysis:
        """
        Perform a complete deterministic financial analysis.

        Parameters
        ----------
        transactions:
            Validated and normalized transaction data.

        goals:
            List of FinancialGoal objects.

        debts:
            List of Debt objects.

        emergency_fund:
            Current emergency-fund balance.

        Returns
        -------
        FinancialAnalysis
            Aggregated financial analysis.
        """

        goals = goals or []
        debts = debts or []

        expense_summary = self.expense_calculator.calculate_summary(transactions)

        monthly_income = expense_summary["income"]
        monthly_expenses = expense_summary["expenses"]
        monthly_surplus = expense_summary["surplus"]
        savings_rate = expense_summary["savings_rate"]

        expense_breakdown = expense_summary["category_breakdown"]
        top_categories = expense_summary["top_categories"]

        budget = self.budget_calculator.generate_budget(
            monthly_income=monthly_income,
            monthly_surplus=monthly_surplus,
            expense_breakdown=expense_breakdown,
        )

        goal_analysis = (
            self.goal_calculator.analyze_all_goals(
                goals,
                monthly_surplus,
            )
        )

        debt_analysis = [
            self.debt_calculator.analyze_debt(debt)
            for debt in debts
        ]

        debt_to_income_ratio = (
            self._calculate_debt_to_income_ratio(
                debts,
                monthly_income,
                transactions,
            )
        )

        emergency_fund_months = (
            self._calculate_emergency_fund_months(
                emergency_fund,
                monthly_expenses,
            )
        )

        financial_health_score = (
            self._calculate_financial_health_score(
                savings_rate=savings_rate,
                debt_to_income_ratio=debt_to_income_ratio,
                emergency_fund_months=emergency_fund_months,
                goal_analysis=goal_analysis,
            )
        )

        return FinancialAnalysis(
            monthly_income=monthly_income,
            monthly_expenses=monthly_expenses,
            monthly_surplus=monthly_surplus,
            savings_rate=savings_rate,
            expense_breakdown=expense_breakdown,
            top_categories=top_categories,
            budget=budget,
            goal_analysis=goal_analysis,
            debt_analysis=debt_analysis,
            debt_to_income_ratio=debt_to_income_ratio,
            emergency_fund_months=emergency_fund_months,
            financial_health_score=financial_health_score,
        )

    def _calculate_debt_to_income_ratio(
        self,
        debts: list[Debt],
        monthly_income: Decimal,
        transactions: TransactionBatch,
    ) -> Decimal:

        if monthly_income <= 0:
            return Decimal("0")

        total_emi = self.debt_calculator.total_monthly_emi(
            debts
        )

        csv_debt_payments = sum(
            (
                transaction.amount
                for transaction in transactions.transactions
                if transaction.transaction_type == TransactionType.DEBIT
                and transaction.category == ExpenseCategory.DEBT
            ),
            Decimal("0"),
        )

        total_emi += csv_debt_payments

        ratio = (
            total_emi
            / monthly_income
            * Decimal("100")
        )

        return self._round(ratio)

    def _calculate_emergency_fund_months(
        self,
        emergency_fund: Decimal,
        monthly_expenses: Decimal,
    ) -> Decimal:

        if monthly_expenses <= 0:
            return Decimal("0")

        months = (
            emergency_fund
            / monthly_expenses
        )

        return self._round(months)

    def _calculate_financial_health_score(
        self,
        savings_rate: Decimal,
        debt_to_income_ratio: Decimal,
        emergency_fund_months: Decimal,
        goal_analysis: list[GoalAnalysis],
    ) -> int:
        """
        Calculate a simple deterministic financial-health score.

        Maximum score: 100

        Savings rate:
            40 points

        Debt-to-income ratio:
            30 points

        Emergency fund:
            20 points

        Goal feasibility:
            10 points
        """

        savings_score = self._savings_score(savings_rate)
        debt_score = self._debt_score(debt_to_income_ratio)
        emergency_score = self._emergency_fund_score(emergency_fund_months)
        goal_score = self._goal_score(goal_analysis)

        return min(
            100,
            max(
                0,
                savings_score
                + debt_score
                + emergency_score
                + goal_score,
            ),
        )

    def _savings_score(
        self,
        savings_rate: Decimal,
    ) -> int:

        if savings_rate >= Decimal("30"):
            return 40

        if savings_rate >= Decimal("20"):
            return 30

        if savings_rate >= Decimal("10"):
            return 20

        if savings_rate > Decimal("0"):
            return 10

        return 0

    def _debt_score(
        self,
        debt_to_income_ratio: Decimal,
    ) -> int:

        if debt_to_income_ratio <= Decimal("10"):
            return 30

        if debt_to_income_ratio <= Decimal("20"):
            return 25

        if debt_to_income_ratio <= Decimal("30"):
            return 20

        if debt_to_income_ratio <= Decimal("40"):
            return 10

        return 0

    def _emergency_fund_score(
        self,
        emergency_fund_months: Decimal,
    ) -> int:

        if emergency_fund_months >= Decimal("6"):
            return 20

        if emergency_fund_months >= Decimal("3"):
            return 15

        if emergency_fund_months >= Decimal("1"):
            return 10

        if emergency_fund_months > Decimal("0"):
            return 5

        return 0

    def _goal_score(
        self,
        goal_analysis,
    ) -> int:

        if not goal_analysis:
            return 10

        feasible_goals = sum(
            analysis.is_feasible
            for analysis in goal_analysis
        )

        feasibility_ratio = (
            Decimal(feasible_goals)
            / Decimal(len(goal_analysis))
        )

        if feasibility_ratio >= Decimal("0.75"):
            return 10

        if feasibility_ratio >= Decimal("0.50"):
            return 7

        if feasibility_ratio > Decimal("0"):
            return 4

        return 0

    def _round(
        self,
        value: Decimal,
    ) -> Decimal:

        return value.quantize(
            Decimal("0.01")
        )
