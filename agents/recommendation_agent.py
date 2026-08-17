"""
LLM-powered financial recommendation agent.
"""

from __future__ import annotations

from agents.llm import LLMManager
from prompts.recommendation_agent import build_recommendation_prompt
from schemas.analysis import FinancialAnalysis


class RecommendationAgent:
    """
    Generates personalized financial recommendations using an Ollama LLM.
    """

    def __init__(self,model: str = "gemma4:31b-cloud",temperature: float = 0.0):

        self.llm = LLMManager(
            model=model,
            temperature=temperature,
        )

    def generate(self, analysis: FinancialAnalysis) -> list[str]:
        """
        Generate financial recommendations.
        """

        prompt = build_recommendation_prompt(analysis)

        response = self.llm.invoke(prompt)

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
