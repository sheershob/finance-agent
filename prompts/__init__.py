"""
Prompt templates used by the LLM-powered agents.
"""
from prompts.recommendation_agent import build_recommendation_prompt
from prompts.report import build_report_prompt

__all__ = [
    "build_recommendation_prompt",
    "build_report_prompt",
]
