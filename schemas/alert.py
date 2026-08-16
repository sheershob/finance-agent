from decimal import Decimal

from pydantic import BaseModel, Field

from .enums import AlertSeverity, ExpenseCategory


class FinancialAlert(BaseModel):
    """
    Represents a financial warning detected by the system.
    """

    title: str = Field(min_length=1)

    description: str

    severity: AlertSeverity

    category: ExpenseCategory | None = None

    current_amount: Decimal | None = Field(
        default=None,
        ge=0
    )

    reference_amount: Decimal | None = Field(
        default=None,
        ge=0
    )

    percentage_change: Decimal | None = None

    recommendation: str | None = None