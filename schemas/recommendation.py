from decimal import Decimal

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """
    Represents an actionable financial recommendation.
    """

    title: str = Field(min_length=1)

    reason: str

    priority: int = Field(
        default=1,
        ge=1
    )

    estimated_monthly_savings: Decimal = Field(
        default=Decimal("0"),
        ge=0
    )

    action_items: list[str] = Field(
        default_factory=list
    )