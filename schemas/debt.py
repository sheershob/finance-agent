from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class Debt(BaseModel):
    """
    Represents a user's outstanding loan/debt.
    """

    loan_name: str = Field(min_length=1)
    outstanding_principal: Decimal = Field(gt=0)

    interest_rate: Decimal = Field(
        ge=0,
        le=100
    )

    remaining_tenure_months: int = Field(gt=0)
    monthly_emi: Decimal = Field(gt=0)
    loan_start_date: date | None = None


class DebtAnalysis(BaseModel):

    debt: Debt
    total_remaining_payment: Decimal
    estimated_remaining_interest: Decimal
    interest_to_principal_ratio: Decimal
    payoff_date: date
    monthly_interest_component: Decimal
    monthly_principal_component: Decimal
    prepayment_savings: Decimal
    prepayment_months_saved: int