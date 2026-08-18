"""
LLM-powered financial report generator.
"""

from __future__ import annotations
from pathlib import Path
import time

from agents.llm import LLMManager
from prompts.report import build_report_prompt
from schemas.analysis import FinancialAnalysis


class ReportAgent:
    """
    Generates a comprehensive financial report
    """

    def __init__(self, model: str | None = None, temperature: float = 0.0):


        self.llm = LLMManager(
            model=model,
            temperature=temperature,
        )
        self.last_generation_seconds: float | None = None

    def generate(self, analysis: FinancialAnalysis) -> str:
        """
        Generate a complete financial report.
        """
        print("\n" + "🤖 " + "=" * 68, flush=True)
        print("[AGENT CALL] ReportAgent.generate", flush=True)
        print("[INPUT DATA]:", flush=True)
        print(f"  Monthly Income:          ₹{analysis.monthly_income}", flush=True)
        print(f"  Monthly Expenses:        ₹{analysis.monthly_expenses}", flush=True)
        print(f"  Monthly Surplus:         ₹{analysis.monthly_surplus}", flush=True)
        print(f"  Savings Rate:            {analysis.savings_rate}%", flush=True)
        print(f"  Debt to Income Ratio:    {analysis.debt_to_income_ratio}%", flush=True)
        print(f"  Emergency Fund Months:   {analysis.emergency_fund_months}", flush=True)
        print(f"  Financial Health Score:  {analysis.financial_health_score}/100", flush=True)
        print("=" * 70, flush=True)

        prompt = build_report_prompt(
            analysis
        )

        start_time = time.perf_counter()
        report = self.llm.invoke(prompt)
        self.last_generation_seconds = time.perf_counter() - start_time

        return report
    def generate_markdown(self, analysis: FinancialAnalysis) -> str:
        """
        Generate a Markdown report.
        """

        return self.generate(analysis)

    def save_report(self, report: str, output_path: str = "reports/financial_report.md") -> str:
        """
        Save the generated Markdown report to disk.

        Returns the path of the saved report.
        """

        output_file = Path(output_path)

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file.write_text(
            report,
            encoding="utf-8",
        )

        return str(output_file)
