from __future__ import annotations

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

class FinancialProfile(BaseModel):
    """
    Stores all long-term financial information about a user.

    This schema represents WHO the user is financially,
    not what happened this month.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )

    monthly_income: Decimal = Field(
        ge=0,
        description="Net monthly income."
    )

    fixed_expenses: Decimal = Field(
        ge=0,
        description="Recurring monthly expenses."
    )

    variable_expenses: Decimal = Field(
        ge=0,
        description="Average monthly variable expenses."
    )

    existing_savings: Decimal = Field(
        ge=0,
        description="Current savings."
    )

    monthly_investment: Decimal = Field(
        ge=0,
        description="Current monthly investment."
    )

    risk_profile: Optional[str] = Field(
        default=None,
        description="Low, Medium or High."
    )

    dependents: int = Field(
        default=0,
        ge=0
    )

    notes: Optional[str] = None
