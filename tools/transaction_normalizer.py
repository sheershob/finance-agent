"""
Normalizes validated transactions into a consistent format.

Responsibilities
----------------
1. Normalize merchant names.
2. Clean descriptions.
3. Standardize capitalization.
4. Remove unnecessary whitespace.
5. Round monetary values.
6. Return a new TransactionBatch.
"""

from __future__ import annotations

import re
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

from schemas.transaction import (
    Transaction,
    TransactionBatch,
)


class TransactionNormalizer:
    """
    Cleans and standardizes validated transactions.
    """

    # ----------------------------------------------------------

    MERCHANT_MAPPING = {

        "amazon india pvt ltd": "Amazon",
        "amazon seller services": "Amazon",
        "swiggy ltd": "Swiggy",
        "zomato limited": "Zomato",
        "uber india": "Uber",
        "ola cabs": "Ola",
        "flipkart internet pvt ltd": "Flipkart",
        "netflix": "Netflix",
        "spotify": "Spotify",
        "google pay": "Google Pay",
        "phonepe": "PhonePe",
        "paytm": "Paytm",

    }

    def normalize(
        self,
        batch: TransactionBatch,
    ) -> TransactionBatch:
        """
        Normalize an entire transaction batch.
        """

        normalized_transactions = []

        for transaction in batch.transactions:

            normalized_transactions.append(
                self.normalize_transaction(
                    transaction
                )
            )

        return TransactionBatch(
            transactions=normalized_transactions
        )

    def normalize_transaction(
        self,
        transaction: Transaction,
    ) -> Transaction:
        """
        Normalize a single transaction.
        """

        transaction = deepcopy(transaction)

        transaction.description = self._normalize_text(
            transaction.description
        )

        transaction.merchant = self._normalize_merchant(
            transaction.merchant
        )

        transaction.amount = self._normalize_amount(
            transaction.amount
        )

        return transaction

    def _normalize_text(
        self,
        text: str,
    ) -> str:
        """
        Remove extra spaces and standardize capitalization.
        """

        text = text.strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.title()

    def _normalize_merchant(
        self,
        merchant: str | None,
    ) -> str | None:

        if merchant is None:

            return None

        merchant = merchant.strip()

        merchant = re.sub(
            r"\s+",
            " ",
            merchant,
        )

        key = merchant.lower()

        if key in self.MERCHANT_MAPPING:

            return self.MERCHANT_MAPPING[key]

        return merchant.title()

    def _normalize_amount(
        self,
        amount: Decimal,
    ) -> Decimal:
        """
        Round to two decimal places.
        """

        return amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )