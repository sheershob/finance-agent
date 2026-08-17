"""
Responsibilities
----------------
1. Validate individual transactions.
2. Validate complete TransactionBatch objects.
3. Detect duplicate transactions.
4. Collect validation errors without stopping at the first failure.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import date
from typing import List, Set, Tuple

from schemas.transaction import (
    Transaction,
    TransactionBatch,
)

from schemas.enums import TransactionType


# ---------------------------------------------------------------------
# Validation Models
# ---------------------------------------------------------------------


@dataclass(slots=True)
class ValidationError:
    """
    Represents a single validation error.
    """

    row: int
    field: str
    message: str


@dataclass(slots=True)
class ValidationResult:
    """
    Output returned after validating a TransactionBatch.

    This object intentionally exposes the same ``transactions`` attribute that
    the downstream pipeline expects from a TransactionBatch, while preserving the
    additional validation metadata.
    """

    valid_transactions: List[Transaction]
    invalid_transactions: List[Transaction]
    errors: List[ValidationError]

    @property
    def transactions(self) -> List[Transaction]:
        return self.valid_transactions

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def as_batch(self) -> TransactionBatch:
        return TransactionBatch(transactions=self.valid_transactions)


# ---------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------

class TransactionValidator:
    """
    Performs validation on Transaction objects.
    """

    def __init__(self, allow_zero_amount: bool = False) -> None:

        self.allow_zero_amount = allow_zero_amount

    # -------------------------------------------------------------

    def validate_batch(self,batch: TransactionBatch) -> ValidationResult:
        """
        Validate an entire batch of transactions.
        """

        valid_transactions: List[Transaction] = []
        invalid_transactions: List[Transaction] = []
        errors: List[ValidationError] = []

        seen: Set[Tuple] = set()

        for row_number, transaction in enumerate(
            batch.transactions,
            start=1,
        ):

            transaction_errors = self.validate_transaction(
                transaction,
                row_number,
            )

            duplicate_error = self._check_duplicate(
                transaction,
                row_number,
                seen,
            )

            if duplicate_error is not None:
                transaction_errors.append(duplicate_error)

            if transaction_errors:

                invalid_transactions.append(transaction)
                errors.extend(transaction_errors)

            else:

                valid_transactions.append(transaction)

        return ValidationResult(
            valid_transactions=valid_transactions,
            invalid_transactions=invalid_transactions,
            errors=errors,
        )

    # -------------------------------------------------------------

    def validate_transaction(self, transaction: Transaction, row_number: int) -> List[ValidationError]:

        errors: List[ValidationError] = []

        if not transaction.description.strip():

            errors.append(
                ValidationError(
                    row=row_number,
                    field="description",
                    message="Description cannot be empty.",
                )
            )

        if self.allow_zero_amount:

            if transaction.amount < Decimal("0"):

                errors.append(
                    ValidationError(
                        row=row_number,
                        field="amount",
                        message="Amount cannot be negative.",
                    )
                )

        else:

            if transaction.amount <= Decimal("0"):

                errors.append(
                    ValidationError(
                        row=row_number,
                        field="amount",
                        message="Amount must be greater than zero.",
                    )
                )

        if transaction.date > date.today():

            errors.append(
                ValidationError(
                    row=row_number,
                    field="date",
                    message="Transaction date cannot be in the future.",
                )
            )

        if (
            transaction.merchant is not None
            and not transaction.merchant.strip()
        ):

            errors.append(
                ValidationError(
                    row=row_number,
                    field="merchant",
                    message="Merchant cannot be blank.",
                )
            )

        if transaction.transaction_type not in (
            TransactionType.CREDIT,
            TransactionType.DEBIT,
        ):

            errors.append(
                ValidationError(
                    row=row_number,
                    field="transaction_type",
                    message="Invalid transaction type.",
                )
            )

        return errors

    # -------------------------------------------------------------

    def _check_duplicate(self,transaction: Transaction, row_number: int, seen: Set[Tuple]) -> ValidationError | None:
        """
        Detect duplicate transactions.

        Duplicate definition:
        Same date + amount + description.
        """

        key = (
            transaction.date,
            transaction.amount,
            transaction.description.lower().strip(),
        )

        if key in seen:

            return ValidationError(
                row=row_number,
                field="transaction",
                message="Duplicate transaction detected.",
            )

        seen.add(key)

        return None