from __future__ import annotations

from datetime import date
from typing import Optional, TypeAlias

from pydantic import BaseModel, Field, ConfigDict

from .enums import ExpenseCategory, TransactionType

class Transaction(BaseModel):
    """
    Represents one financial transaction.
    """
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )

    date: date
    description: str

    amount: float = Field(gt=0)

    transaction_type: TransactionType
    reference_number: str | None = None
    category: ExpenseCategory = ExpenseCategory.OTHER
    merchant: Optional[str] = None
    source_file: Optional[str] = None
    notes: Optional[str] = None


# A batch is the validated list of transactions passed through the workflow.
# Define this after Transaction so type-hint evaluation never receives a
# forward reference from a different module's namespace.
TransactionBatch: TypeAlias = list[Transaction]
