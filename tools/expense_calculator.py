"""
Performs deterministic financial calculations on transactions.

This tool does NOT perform any AI reasoning.
It simply computes financial statistics that other agents
can use.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from schemas.transaction import TransactionBatch
from schemas.enums import (
    TransactionType,
    ExpenseCategory,
)
from schemas.common import CategoryAmount

class ExpenseCalculator:

    """
    Performs expense calculations.
    """
    def total_income(self, batch: TransactionBatch) -> Decimal:

        income = Decimal("0")

        for tx in batch.transactions:

            if tx.transaction_type == TransactionType.CREDIT:

                income += Decimal(str(tx.amount))

        return income
    
    def total_expenses(self, batch: TransactionBatch) -> Decimal:

        expense = Decimal("0")

        for tx in batch.transactions:

            if tx.transaction_type == TransactionType.DEBIT:

                expense += Decimal(str(tx.amount))

        return expense

    def monthly_surplus(self, batch: TransactionBatch) -> Decimal:

        return (
            self.total_income(batch)
            - self.total_expenses(batch)
        )

    def savings_rate(self, batch: TransactionBatch) -> Decimal:

        income = self.total_income(batch)

        if income == Decimal("0"):

            return Decimal("0")

        surplus = self.monthly_surplus(batch)

        return (
            surplus / income * Decimal("100")
        ).quantize(
            Decimal("0.01")
        )

    def category_breakdown(
        self,
        batch: TransactionBatch,
    ) -> list[CategoryAmount]:

        categories = defaultdict(Decimal)

        for tx in batch.transactions:

            if tx.transaction_type == TransactionType.DEBIT:

                categories[tx.category] += Decimal(str(tx.amount))

        breakdown = []

        for category, amount in categories.items():

            breakdown.append(

                CategoryAmount(

                    category=category.value,

                    amount=amount,

                )

            )

        return breakdown

    def top_categories(
        self,
        batch: TransactionBatch,
        top_n: int = 5,
    ) -> list[CategoryAmount]:

        breakdown = self.category_breakdown(batch)

        breakdown.sort(

            key=lambda x: x.amount,

            reverse=True,

        )

        return breakdown[:top_n]
    
    def daily_average_expense(
        self,
        batch: TransactionBatch,
    ) -> Decimal:

        expenses = [

            tx

            for tx in batch.transactions

            if tx.transaction_type == TransactionType.DEBIT

        ]

        if not expenses:

            return Decimal("0")

        total = sum(

            Decimal(str(tx.amount))

            for tx in expenses

        )

        unique_days = len(

            {

                tx.date

                for tx in expenses

            }

        )

        if unique_days == 0:

            return Decimal("0")

        return (total / Decimal(unique_days)).quantize(Decimal("0.01"))

    def monthly_spending(self, batch: TransactionBatch) -> dict[str, Decimal]:

        monthly = defaultdict(Decimal)

        for tx in batch.transactions:

            if tx.transaction_type == TransactionType.DEBIT:

                month = tx.date.strftime("%Y-%m")

                monthly[month] += Decimal(str(tx.amount))

        return dict(monthly)

    # ---------------------------------------------------------

    def calculate_summary(self, batch: TransactionBatch) -> dict:

        return {

            "income": self.total_income(batch),

            "expenses": self.total_expenses(batch),

            "surplus": self.monthly_surplus(batch),

            "savings_rate": self.savings_rate(batch),

            "top_categories": self.top_categories(batch),

            "category_breakdown": self.category_breakdown(batch),

            "daily_average": self.daily_average_expense(batch),

            "monthly_spending": self.monthly_spending(batch),
        }