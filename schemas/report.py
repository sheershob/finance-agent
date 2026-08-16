from decimal import Decimal

from pydantic import BaseModel, Field

from .alert import FinancialAlert
from .analysis import FinancialAnalysis
from .budget import MonthlyBudget
from .enums import FinancialHealth
from .goal import FinancialGoal
from .recommendation import Recommendation


class MonthlyReport(BaseModel):

    analysis: FinancialAnalysis

    budget: MonthlyBudget | None = None

    goals: list[FinancialGoal] = Field(default_factory=list)

    alerts: list[FinancialAlert] = Field(default_factory=list)

    recommendations: list[Recommendation] = Field(
        default_factory=list
    )

    overall_health: FinancialHealth

    summary: str
