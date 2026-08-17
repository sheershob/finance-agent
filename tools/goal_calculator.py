"""
Performs deterministic calculations for financial goals.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from dateutil.relativedelta import relativedelta

from schemas.goal import FinancialGoal, GoalAnalysis


class GoalCalculator:

    def analyze_goal(
        self,
        goal: FinancialGoal,
        monthly_surplus: Decimal,
    ) -> GoalAnalysis:

        required_monthly = self.required_monthly_saving(goal)

        funding_gap = self.funding_gap(
            goal,
            monthly_surplus,
        )

        progress = self.progress_percentage(goal)

        feasible = monthly_surplus >= required_monthly

        completion = self.projected_completion_date(
            goal,
            monthly_surplus,
        )

        return GoalAnalysis(
            goal=goal,
            required_monthly_saving=required_monthly,
            projected_completion_date=completion,
            funding_gap=funding_gap,
            progress_percentage=progress,
            is_feasible=feasible,
        )

    def required_monthly_saving(
        self,
        goal: FinancialGoal,
    ) -> Decimal:

        remaining = max(
            goal.target_amount - goal.current_amount,
            Decimal("0"),
        )

        months = max(goal.time_horizon_months, 1)

        return self._round(
            remaining / Decimal(months)
        )

    def funding_gap(
        self,
        goal: FinancialGoal,
        monthly_surplus: Decimal,
    ) -> Decimal:

        gap = (
            self.required_monthly_saving(goal)
            - monthly_surplus
        )

        return self._round(
            max(gap, Decimal("0"))
        )

    def progress_percentage(
        self,
        goal: FinancialGoal,
    ) -> Decimal:

        if goal.target_amount == 0:
            return Decimal("0")

        progress = (
            goal.current_amount
            / goal.target_amount
        ) * Decimal("100")

        return self._round(progress)

    def projected_completion_date(
        self,
        goal: FinancialGoal,
        monthly_surplus: Decimal,
    ) -> date:

        remaining = max(
            goal.target_amount - goal.current_amount,
            Decimal("0"),
        )

        if monthly_surplus <= 0:
            return date.max

        months = int(
            remaining / monthly_surplus
        )

        return date.today() + relativedelta(
            months=months
        )

    def analyze_all_goals(
        self,
        goals: list[FinancialGoal],
        monthly_surplus: Decimal,
    ) -> list[GoalAnalysis]:

        return [
            self.analyze_goal(
                goal,
                monthly_surplus,
            )
            for goal in goals
        ]

    def total_goal_amount(
        self,
        goals: list[FinancialGoal],
    ) -> Decimal:

        return self._round(
            sum(
                (goal.target_amount for goal in goals),
                Decimal("0"),
            )
        )

    def total_current_savings(
        self,
        goals: list[FinancialGoal],
    ) -> Decimal:

        return self._round(
            sum(
                (goal.current_amount for goal in goals),
                Decimal("0"),
            )
        )

    def total_remaining_amount(
        self,
        goals: list[FinancialGoal],
    ) -> Decimal:

        total = sum(
            max(
                goal.target_amount - goal.current_amount,
                Decimal("0"),
            )
            for goal in goals
        )

        return self._round(total)

    def goal_summary(
        self,
        analyses: list[GoalAnalysis],
    ) -> dict:

        feasible = sum(
            analysis.is_feasible
            for analysis in analyses
        )

        return {
            "total_goals": len(analyses),
            "feasible_goals": feasible,
            "infeasible_goals": len(analyses) - feasible,
            "goal_completion_rate": self._round(
                Decimal(feasible)
                / Decimal(max(len(analyses), 1))
                * Decimal("100")
            ),
        }

    def _round(
        self,
        value: Decimal,
    ) -> Decimal:

        return value.quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )
