from typing import Any

from pydantic import BaseModel, Field

from .alert import FinancialAlert
from .analysis import FinancialAnalysis
from .budget import MonthlyBudget
from .debt import Debt, DebtAnalysis
from .goal import FinancialGoal
from .profile import FinancialProfile
from .recommendation import Recommendation
from .report import MonthlyReport
from .transaction import TransactionBatch


class FinanceAgentState(BaseModel):
    """
    Shared state passed between agents in the LangGraph workflow.
    """

    user_query: str | None = None
    profile: FinancialProfile | None = None
    transactions: TransactionBatch | None = None
    analysis: FinancialAnalysis | None = None
    budget: MonthlyBudget | None = None
    goals: list[FinancialGoal] = Field(default_factory=list)
    debts: list[Debt] = Field(default_factory=list)
    debt_analysis: list[DebtAnalysis] = Field(default_factory=list)
    alerts: list[FinancialAlert] = Field(default_factory=list)
    recommendations: list[Recommendation] = Field(default_factory=list)
    report: MonthlyReport | None = None
    final_response: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    """
    The graph flow of data between agents is as follows:

                 FinanceAgentState
                        │
                        ▼
                 Profile Agent
                        │
                 state.profile
                        │
                        ▼
              Transaction Agent
                        │
              state.transactions
                        │
                        ▼
             Categorization Agent
                        │
                        ▼
               Analysis Agent
                        │
                state.analysis
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
          Budget      Goal       Debt
           state       state      state
             │          │          │
             └──────────┼──────────┘
                        ▼
               Recommendation
                        │
                        ▼
                    Report
    """
