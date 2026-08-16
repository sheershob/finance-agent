from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

class FinancialGoal(BaseModel):
    """
    Represents a user's financial goal.
    """

    name: str = Field(
        ...,
        description="Name of the financial goal."
    )

    target_amount: Decimal = Field(
        ...,
        gt=0,
        description="Target amount to be achieved."
    )

    current_amount: Decimal = Field(
        default=Decimal("0"),
        ge=0,
        description="Current savings towards the goal."
    )

    target_date: Optional[date] = Field(
        default=None,
        description="Desired completion date."
    )

    time_horizon_months: int = Field(
        ...,
        gt=0,
        description="Time available to achieve the goal in months."
    )

    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Priority of the goal (1 = highest, 5 = lowest)."
    )

    category: Optional[str] = Field(
        default=None,
        description="Goal category (Retirement, Vacation, Emergency Fund, House, etc.)."
    )

    notes: Optional[str] = Field(
        default=None,
        description="Additional user notes."
    )

# class Goal(BaseModel):
#     """
#     Represents a financial goal defined by the user.
#     """

#     name: str = Field(min_length=1)

#     goal_type: GoalType

#     target_amount: Decimal = Field(gt=0)

#     current_amount: Decimal = Field(
#         default=Decimal("0"),
#         ge=0
#     )

#     timeline_months: int = Field(gt=0)

#     monthly_required: Decimal = Field(
#         default=Decimal("0"),
#         ge=0
#     )

#     priority: int = Field(
#         default=1,
#         ge=1
#     )

#     status: GoalStatus = GoalStatus.AT_RISK

class GoalAnalysis(BaseModel):

    goal: FinancialGoal
    required_monthly_saving: Decimal
    projected_completion_date: date
    funding_gap: Decimal
    progress_percentage: Decimal
    is_feasible: bool
