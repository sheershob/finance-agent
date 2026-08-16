"""
This is for small reusable models.
"""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class DateRange(BaseModel):
    start_date: date
    end_date: date


class CategoryAmount(BaseModel):
    category: str
    amount: Decimal = Field(ge=0)