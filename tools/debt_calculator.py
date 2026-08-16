"""
Deterministic calculations for loans and debts.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from schemas.debt import Debt, DebtAnalysis


class DebtCalculator:

    def analyze_debt(
        self,
        debt: Debt,
        extra_monthly_payment: Decimal = Decimal("0"),
    ) -> DebtAnalysis:

        total_remaining_payment = self.total_remaining_payment(debt)

        remaining_interest = self.remaining_interest(debt)

        interest_ratio = self.interest_ratio(debt)

        payoff_date = self.payoff_date(debt)

        principal_component = self.monthly_principal_component(debt)

        interest_component = self.monthly_interest_component(debt)

        (
            prepayment_savings,
            months_saved,
        ) = self.prepayment_analysis(
            debt,
            extra_monthly_payment,
        )

        return DebtAnalysis(
            debt=debt,
            total_remaining_payment=total_remaining_payment,
            estimated_remaining_interest=remaining_interest,
            interest_to_principal_ratio=interest_ratio,
            payoff_date=payoff_date,
            monthly_interest_component=interest_component,
            monthly_principal_component=principal_component,
            prepayment_savings=prepayment_savings,
            prepayment_months_saved=months_saved,
        )

    def total_remaining_payment(
        self,
        debt: Debt,
    ) -> Decimal:

        return self._round(
            debt.monthly_emi
            * Decimal(debt.remaining_tenure_months)
        )

    def remaining_interest(
        self,
        debt: Debt,
    ) -> Decimal:

        interest = (
            self.total_remaining_payment(debt)
            - debt.outstanding_principal
        )

        return self._round(max(interest, Decimal("0")))

    def interest_ratio(
        self,
        debt: Debt,
    ) -> Decimal:

        if debt.outstanding_principal == 0:
            return Decimal("0")

        ratio = (
            self.remaining_interest(debt)
            / debt.outstanding_principal
        ) * Decimal("100")

        return self._round(ratio)

    def payoff_date(
        self,
        debt: Debt,
    ) -> date:

        return date.today() + relativedelta(
            months=debt.remaining_tenure_months
        )

    def monthly_interest_component(
        self,
        debt: Debt,
    ) -> Decimal:

        monthly_rate = (
            debt.interest_rate
            / Decimal("12")
            / Decimal("100")
        )

        interest = (
            debt.outstanding_principal
            * monthly_rate
        )

        return self._round(interest)

    def monthly_principal_component(
        self,
        debt: Debt,
    ) -> Decimal:

        principal = (
            debt.monthly_emi
            - self.monthly_interest_component(debt)
        )

        return self._round(
            max(principal, Decimal("0"))
        )

    def prepayment_analysis(
        self,
        debt: Debt,
        extra_payment: Decimal,
    ) -> tuple[Decimal, int]:

        if extra_payment <= 0:

            return (
                Decimal("0"),
                0,
            )

        monthly_principal = (
            self.monthly_principal_component(debt)
            + extra_payment
        )

        if monthly_principal <= 0:

            return (
                Decimal("0"),
                0,
            )

        estimated_months = int(
            debt.outstanding_principal
            / monthly_principal
        )

        months_saved = max(
            debt.remaining_tenure_months
            - estimated_months,
            0,
        )

        monthly_interest = (
            self.monthly_interest_component(debt)
        )

        interest_saved = (
            monthly_interest
            * Decimal(months_saved)
        )

        return (
            self._round(interest_saved),
            months_saved,
        )

    def total_outstanding_principal(
        self,
        debts: list[Debt],
    ) -> Decimal:

        total = sum(
            debt.outstanding_principal
            for debt in debts
        )

        return self._round(total)

    def total_monthly_emi(
        self,
        debts: list[Debt],
    ) -> Decimal:

        total = sum(
            debt.monthly_emi
            for debt in debts
        )

        return self._round(total)

    def total_remaining_interest(
        self,
        debts: list[Debt],
    ) -> Decimal:

        total = sum(
            self.remaining_interest(debt)
            for debt in debts
        )

        return self._round(total)

    def debt_summary(
        self,
        analysis: DebtAnalysis,
    ) -> str:

        return (
            f"""
Loan Name                : {analysis.debt.loan_name}
Outstanding Principal    : ₹{analysis.debt.outstanding_principal}
Interest Rate            : {analysis.debt.interest_rate}%
Remaining Tenure         : {analysis.debt.remaining_tenure_months} months
Monthly EMI              : ₹{analysis.debt.monthly_emi}

Remaining Interest       : ₹{analysis.estimated_remaining_interest}
Total Remaining Payment  : ₹{analysis.total_remaining_payment}

Interest Ratio           : {analysis.interest_to_principal_ratio}%

Monthly Principal        : ₹{analysis.monthly_principal_component}
Monthly Interest         : ₹{analysis.monthly_interest_component}

Estimated Payoff         : {analysis.payoff_date}

Interest Saved           : ₹{analysis.prepayment_savings}
Months Saved             : {analysis.prepayment_months_saved}
""".strip()
        )

    def debt_as_dict(
        self,
        analysis: DebtAnalysis,
    ) -> dict:

        return {
            "loan_name": analysis.debt.loan_name,
            "principal": analysis.debt.outstanding_principal,
            "interest_rate": analysis.debt.interest_rate,
            "remaining_tenure": analysis.debt.remaining_tenure_months,
            "monthly_emi": analysis.debt.monthly_emi,
            "remaining_interest": analysis.estimated_remaining_interest,
            "total_payment": analysis.total_remaining_payment,
            "interest_ratio": analysis.interest_to_principal_ratio,
            "monthly_principal": analysis.monthly_principal_component,
            "monthly_interest": analysis.monthly_interest_component,
            "payoff_date": analysis.payoff_date,
            "prepayment_savings": analysis.prepayment_savings,
            "months_saved": analysis.prepayment_months_saved,
        }

    def _round(
        self,
        value: Decimal,
    ) -> Decimal:

        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )