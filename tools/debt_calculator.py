"""
Deterministic calculations for loans and debts using true loan amortization schedules.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from schemas.debt import Debt, DebtAnalysis


class DebtCalculator:
    """
    Performs deterministic financial calculations and true amortization schedule
    analysis for debts and loans.
    """

    def run_amortization_schedule(
        self,
        outstanding_principal: Decimal,
        interest_rate: Decimal,
        monthly_emi: Decimal,
        remaining_tenure_months: int,
    ) -> tuple[Decimal, Decimal, Decimal, Decimal, list[dict]]:
        """
        Simulates a true month-by-month loan amortization schedule over the remaining tenure.

        Returns
        -------
        tuple[Decimal, Decimal, Decimal, Decimal, list[dict]]
            (total_payment, total_interest, month1_principal, month1_interest, schedule)
        """
        if remaining_tenure_months <= 0 or outstanding_principal <= 0:
            return Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), []

        monthly_rate = interest_rate / Decimal("12") / Decimal("100")
        current_balance = outstanding_principal
        total_interest = Decimal("0")
        total_payment = Decimal("0")
        month1_principal = Decimal("0")
        month1_interest = Decimal("0")
        schedule = []

        for month in range(1, remaining_tenure_months + 1):
            if current_balance <= 0:
                break

            # Calculate interest for the current month's remaining balance
            interest_for_month = current_balance * monthly_rate

            # Determine payment for this month (capped at remaining principal + interest)
            payment_amount = min(monthly_emi, current_balance + interest_for_month)

            if payment_amount <= interest_for_month:
                # EMI is less than or equal to accrued monthly interest
                interest_paid = payment_amount
                principal_for_month = Decimal("0")
            else:
                interest_paid = interest_for_month
                principal_for_month = min(payment_amount - interest_paid, current_balance)

            current_balance -= principal_for_month
            total_interest += interest_paid
            total_payment += payment_amount

            if month == 1:
                month1_principal = principal_for_month
                month1_interest = interest_paid

            schedule.append({
                "month": month,
                "payment": payment_amount,
                "principal": principal_for_month,
                "interest": interest_paid,
                "remaining_balance": current_balance,
            })

        return (
            total_payment,
            total_interest,
            month1_principal,
            month1_interest,
            schedule,
        )

    def analyze_debt(
        self,
        debt: Debt,
        extra_monthly_payment: Decimal = Decimal("0"),
    ) -> DebtAnalysis:
        """
        Perform complete deterministic debt analysis using true amortization.
        """
        # Flag if EMI * tenure < outstanding principal
        is_insufficient = False
        warning_message = None

        tenure_total_emi = debt.monthly_emi * Decimal(debt.remaining_tenure_months)
        if tenure_total_emi < debt.outstanding_principal:
            is_insufficient = True
            warning_message = "EMI/tenure insufficient to repay principal."

        # Run true amortization schedule
        (
            total_payment,
            total_interest,
            month1_principal,
            month1_interest,
            _,
        ) = self.run_amortization_schedule(
            outstanding_principal=debt.outstanding_principal,
            interest_rate=debt.interest_rate,
            monthly_emi=debt.monthly_emi,
            remaining_tenure_months=debt.remaining_tenure_months,
        )

        total_remaining_payment = self._round(total_payment)
        remaining_interest = self._round(total_interest)

        if debt.outstanding_principal > 0:
            interest_ratio = self._round(
                (remaining_interest / debt.outstanding_principal) * Decimal("100")
            )
        else:
            interest_ratio = Decimal("0")

        payoff_date = self.payoff_date(debt)

        principal_component = self._round(month1_principal)
        interest_component = self._round(month1_interest)

        (
            prepayment_savings,
            months_saved,
        ) = self.prepayment_analysis(
            debt,
            extra_monthly_payment,
            total_interest,
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
            is_insufficient=is_insufficient,
            warning_message=warning_message,
        )

    def total_remaining_payment(
        self,
        debt: Debt,
    ) -> Decimal:
        tot_pay, _, _, _, _ = self.run_amortization_schedule(
            debt.outstanding_principal,
            debt.interest_rate,
            debt.monthly_emi,
            debt.remaining_tenure_months,
        )
        return self._round(tot_pay)

    def remaining_interest(
        self,
        debt: Debt,
    ) -> Decimal:
        _, tot_int, _, _, _ = self.run_amortization_schedule(
            debt.outstanding_principal,
            debt.interest_rate,
            debt.monthly_emi,
            debt.remaining_tenure_months,
        )
        return self._round(tot_int)

    def interest_ratio(
        self,
        debt: Debt,
    ) -> Decimal:
        if debt.outstanding_principal == 0:
            return Decimal("0")

        rem_int = self.remaining_interest(debt)
        ratio = (rem_int / debt.outstanding_principal) * Decimal("100")
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
            debt.interest_rate / Decimal("12") / Decimal("100")
        )
        return self._round(debt.outstanding_principal * monthly_rate)

    def monthly_principal_component(
        self,
        debt: Debt,
    ) -> Decimal:
        interest = self.monthly_interest_component(debt)
        principal = debt.monthly_emi - interest
        return self._round(max(principal, Decimal("0")))

    def prepayment_analysis(
        self,
        debt: Debt,
        extra_payment: Decimal,
        base_total_interest: Decimal | None = None,
    ) -> tuple[Decimal, int]:
        if extra_payment <= 0:
            return Decimal("0"), 0

        if base_total_interest is None:
            base_total_interest = self.remaining_interest(debt)

        accelerated_emi = debt.monthly_emi + extra_payment

        (
            _,
            acc_interest,
            _,
            _,
            acc_schedule,
        ) = self.run_amortization_schedule(
            outstanding_principal=debt.outstanding_principal,
            interest_rate=debt.interest_rate,
            monthly_emi=accelerated_emi,
            remaining_tenure_months=debt.remaining_tenure_months,
        )

        acc_months = len(acc_schedule)
        months_saved = max(debt.remaining_tenure_months - acc_months, 0)
        interest_saved = max(base_total_interest - acc_interest, Decimal("0"))

        return self._round(interest_saved), months_saved

    def total_outstanding_principal(
        self,
        debts: list[Debt],
    ) -> Decimal:
        total = sum(
            (debt.outstanding_principal for debt in debts),
            Decimal("0"),
        )
        return self._round(total)

    def total_monthly_emi(
        self,
        debts: list[Debt],
    ) -> Decimal:
        total = sum(
            (debt.monthly_emi for debt in debts),
            Decimal("0"),
        )
        return self._round(total)

    def total_remaining_interest(
        self,
        debts: list[Debt],
    ) -> Decimal:
        total = sum(
            (self.remaining_interest(debt) for debt in debts),
            Decimal("0"),
        )
        return self._round(total)

    def debt_summary(
        self,
        analysis: DebtAnalysis,
    ) -> str:
        warning_str = f"\nWarning                  : ⚠️ {analysis.warning_message}" if analysis.is_insufficient else ""
        return (
            f"""
Loan Name                : {analysis.debt.loan_name}
Outstanding Principal    : ₹{analysis.debt.outstanding_principal}
Interest Rate            : {analysis.debt.interest_rate}%
Remaining Tenure         : {analysis.debt.remaining_tenure_months} months
Monthly EMI              : ₹{analysis.debt.monthly_emi}
{warning_str}
Remaining Interest       : ₹{analysis.estimated_remaining_interest}
Total Remaining Payment  : ₹{analysis.total_remaining_payment}

Interest Ratio           : {analysis.interest_to_principal_ratio}%

Monthly Principal (M1)   : ₹{analysis.monthly_principal_component}
Monthly Interest (M1)    : ₹{analysis.monthly_interest_component}

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
            "is_insufficient": analysis.is_insufficient,
            "warning_message": analysis.warning_message,
        }

    def _round(
        self,
        value: Decimal,
    ) -> Decimal:
        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
