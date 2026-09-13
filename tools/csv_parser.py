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

    CATEGORY_KEYWORDS = {
        ExpenseCategory.INCOME: ("salary", "bonus", "income", "deposit"),
        ExpenseCategory.SAVINGS: ("savings", "investment", "mutual fund", "stock", "shares"),
        ExpenseCategory.DEBT: ("loan", "credit card", "debt", "repayment", "EMI", "car loan", "home loan"),
        ExpenseCategory.HOUSING: ("rent", "mortgage", "housing", "property"),
        ExpenseCategory.FOOD: (
            "grocery",
            "groceries",
            "restaurant",
            "cafe",
            "coffee",
            "food",
            "swiggy",
            "zomato",
        ),
        ExpenseCategory.TRANSPORTATION: (
            "uber",
            "ola",
            "rapido",
            "fuel",
            "petrol",
            "diesel",
            "CNG",
            "gas station",
            "transport",
            "metro",
            "bus",
            "train",
            "cab",
            "auto",
            "taxi",
        ),
        ExpenseCategory.SHOPPING: (
            "amazon",
            "flipkart",
            "shopping",
            "retail",
            "mall",
        ),
        ExpenseCategory.ENTERTAINMENT: (
            "netflix",
            "spotify",
            "movie",
            "cinema",
            "entertainment",
        ),
        ExpenseCategory.UTILITIES: (
            "electricity",
            "water bill",
            "gas bill",
            "repair",
            "internet",
            "broadband",
            "phone bill",
            "mobile bill",
            "utility",
        ),
        ExpenseCategory.HEALTHCARE: (
            "hospital",
            "doctor",
            "pharmacy",
            "medical",
            "health",
        ),
        ExpenseCategory.EDUCATION: (
            "school",
            "college",
            "university",
            "course",
            "tuition",
            "education",
        ),
        ExpenseCategory.TRAVEL: (
            "hotel",
            "flight",
            "airline",
            "travel",
            "booking.com",
        ),
        ExpenseCategory.INVESTMENTS: (
            "investment",
            "mutual fund",
            "stock",
            "shares",
            "gold",
            "silver",
            "crypto",
            "bitcoin",
            "brokerage",
        ),
    }

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
                merchant=self._optional_text(
                    row["merchant"] if "merchant" in dataframe.columns else None
                ),
                notes=self._optional_text(
                    row["notes"] if "notes" in dataframe.columns else None
                ),
                category=self._parse_category(
                    row["category"] if "category" in dataframe.columns else None,
                    description=str(row["description"]).strip(),
                    merchant=(
                        str(row["merchant"]).strip()
                        if "merchant" in dataframe.columns and not pd.isna(row["merchant"])
                        else None
                    ),
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

    def _parse_category(
        self,
        value,
        description: str,
        merchant: str | None,
    ) -> ExpenseCategory:

        if value is not None and not pd.isna(value):
            normalized = str(value).strip().casefold()

            for category in ExpenseCategory:
                if normalized == category.value.casefold():
                    return category

            return ExpenseCategory.OTHER

        searchable_text = " ".join(
            text.casefold()
            for text in (description, merchant or "")
            if text
        )

        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if any(keyword in searchable_text for keyword in keywords):
                return category

        return ExpenseCategory.OTHER

    def _optional_text(self, value) -> str | None:
        """Return optional CSV text without converting missing values to 'nan'."""
        if value is None or pd.isna(value):
            return None

        text = str(value).strip()
        return text or None
