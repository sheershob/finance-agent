"""
LLM-powered financial recommendation agent.
"""

from __future__ import annotations
import time

from agents.llm import LLMManager
from prompts.recommendation_agent import build_recommendation_prompt
from schemas.analysis import FinancialAnalysis


class RecommendationAgent:
    """
    Generates personalized financial recommendations using an Ollama LLM.
    """

    def __init__(self, model: str | None = None, temperature: float = 0.0):


        self.llm = LLMManager(
            model=model,
            temperature=temperature,
        )
        self.last_generation_seconds: float | None = None

    def generate(self, analysis: FinancialAnalysis) -> list[str]:
        """
        Generate financial recommendations.
        """
        print("\n" + "🤖 " + "=" * 68, flush=True)
        print("[AGENT CALL] RecommendationAgent.generate", flush=True)
        print("[INPUT DATA]:", flush=True)
        print(f"  Monthly Income:          ₹{analysis.monthly_income}", flush=True)
        print(f"  Monthly Expenses:        ₹{analysis.monthly_expenses}", flush=True)
        print(f"  Monthly Surplus:         ₹{analysis.monthly_surplus}", flush=True)
        print(f"  Savings Rate:            {analysis.savings_rate}%", flush=True)
        print(f"  Debt to Income Ratio:    {analysis.debt_to_income_ratio}%", flush=True)
        print(f"  Emergency Fund Months:   {analysis.emergency_fund_months}", flush=True)
        print(f"  Financial Health Score:  {analysis.financial_health_score}/100", flush=True)
        print("=" * 70, flush=True)

        prompt = build_recommendation_prompt(analysis)

        start_time = time.perf_counter()
        response = self.llm.invoke(prompt)
        self.last_generation_seconds = time.perf_counter() - start_time

        return self._parse_response(response)
    def _parse_response(self, response: str) -> list[str]:
        """
        Convert the LLM output into a clean list
        of recommendations.
        """

        recommendations = []

        for line in response.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("-"):
                line = line[1:].strip()

            elif line.startswith("*"):
                line = line[1:].strip()

            recommendations.append(line)

        return recommendations

    def generate_markdown(
        self,
        analysis: FinancialAnalysis,
    ) -> str:
        """
        Generate recommendations as markdown.
        """

        prompt = build_recommendation_prompt(
            analysis
        )

        return self.llm.invoke(prompt)
