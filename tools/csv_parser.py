"""
Reads a CSV file and converts it into a validated
TransactionBatch object.

Expected CSV format:

date,description,amount,type
01-08-2026,Salary,150000,Credit
02-08-2026,Rent,25000,Debit
03-08-2026,Amazon,4500,Debit
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime
from decimal import Decimal

import pandas as pd

from schemas.transaction import (
    Transaction,
    TransactionBatch,
)

from schemas.enums import (
    TransactionType,
    ExpenseCategory,
)


class CSVParser:
    """
    Parses transaction CSV files into TransactionBatch objects.
    """

    REQUIRED_COLUMNS = {
        "date",
        "description",
        "amount",
        "type",
    }

    DATE_FORMATS = (
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%y",
    )

    def parse(self,file_path: str | Path) -> TransactionBatch:
        """
        Parse a CSV file into a TransactionBatch.

        Parameters
        ----------
        file_path : str | Path

        Returns
        -------
        TransactionBatch
        """

        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        dataframe = pd.read_csv(file_path)

        print("CSV columns:", list(dataframe.columns), flush=True)

        dataframe.columns = (
            dataframe.columns
            .str.strip()
            .str.lower()
        )

        self._validate_columns(dataframe)

        transactions = []

        for _, row in dataframe.iterrows():

            transaction = Transaction(
                date=self._parse_date(row["date"]),
                description=str(row["description"]).strip(),
                amount=self._parse_amount(row["amount"]),
                transaction_type=self._parse_transaction_type(
                    row["type"]
                ),
                category=ExpenseCategory.OTHER,
                merchant=self._optional_text(
                    row["merchant"] if "merchant" in dataframe.columns else None
                ),
                notes=self._optional_text(
                    row["notes"] if "notes" in dataframe.columns else None
                ),
                source_file=file_path.name,
            )

            transactions.append(transaction)

        return TransactionBatch(transactions=transactions)

    def _validate_columns(self,dataframe: pd.DataFrame) -> None:

        columns = set(dataframe.columns)

        missing = self.REQUIRED_COLUMNS - columns

        if missing:

            raise ValueError(
                f"Missing required columns: {missing}"
            )
        
    def _parse_date(self,value: str):

        value = str(value).strip()

        for fmt in self.DATE_FORMATS:

            try:
                return datetime.strptime(
                    value,
                    fmt,
                ).date()

            except ValueError:
                continue

        raise ValueError(
            f"Unsupported date format: {value}"
        )

    def _parse_amount(self,value) -> Decimal:

        if pd.isna(value):
            raise ValueError("Amount cannot be empty.")

        value = (
            str(value)
            .replace(",", "")
            .replace("₹", "")
            .replace("Rs.", "")
            .strip()
        )

        return Decimal(value)

    def _parse_transaction_type(self,value) -> TransactionType:

        value = str(value).strip().lower()

        mapping = {

            "credit": TransactionType.CREDIT,
            "cr": TransactionType.CREDIT,
            "deposit": TransactionType.CREDIT,
            "income": TransactionType.CREDIT,
            "debit": TransactionType.DEBIT,
            "dr": TransactionType.DEBIT,
            "withdrawal": TransactionType.DEBIT,
        }

        if value not in mapping:

            raise ValueError(
                f"Invalid transaction type: {value}"
            )

        return mapping[value]

    def _optional_text(self, value) -> str | None:
        """Return optional CSV text without converting missing values to 'nan'."""
        if value is None or pd.isna(value):
            return None

        text = str(value).strip()
        return text or None
