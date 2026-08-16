from enum import Enum


class TransactionType(str, Enum):
    CREDIT = "Credit"
    DEBIT = "Debit"


class ExpenseCategory(str, Enum):
    HOUSING = "Housing"
    FOOD = "Food"
    TRANSPORTATION = "Transportation"
    SHOPPING = "Shopping"
    ENTERTAINMENT = "Entertainment"
    UTILITIES = "Utilities"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    INVESTMENTS = "Investments"
    OTHER = "Other"


class GoalType(str, Enum):
    HOUSE = "House"
    EMERGENCY_FUND = "Emergency Fund"
    RETIREMENT = "Retirement"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    OTHER = "Other"


class GoalStatus(str, Enum):
    ON_TRACK = "On Track"
    AT_RISK = "At Risk"
    NOT_ON_TRACK = "Not On Track"
    COMPLETED = "Completed"


class RiskProfile(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class AlertSeverity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class FinancialHealth(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    FAIR = "Fair"
    POOR = "Poor"