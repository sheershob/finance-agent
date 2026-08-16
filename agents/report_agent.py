"""
LLM-powered financial report generator.
"""

from __future__ import annotations

from agents.llm import LLMManager
from prompts.report import build_report_prompt
from schemas.analysis import FinancialAnalysis


class ReportAgent:
    """
    Generates a comprehensive financial report
    """

    def __init__(
        self,
        model: str = "qwen2.5:7b",
        temperature: float = 0.0,
    ):

        self.llm = LLMManager(
            model=model,
            temperature=temperature,
        )

    def generate(self, analysis: FinancialAnalysis) -> str:
        """
        Generate a complete financial report.
        """

        prompt = build_report_prompt(
            analysis
        )

        return self.llm.invoke(prompt)

    def generate_markdown(self, analysis: FinancialAnalysis) -> str:
        """
        Generate a Markdown report.
        """

        return self.generate(analysis)

    def save_report(
        self,
        report: str,
        output_path: str,
    ) -> None:
        """
        Save the generated report to disk.
        """

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as file:

            file.write(report)
