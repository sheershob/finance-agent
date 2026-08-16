"""
Centralized Ollama LLM configuration.
All agents should obtain their LLM instance
through this module instead of creating
their own model.
"""

from __future__ import annotations

import os

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL","gemma4:31b-cloud ")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE","0.0"))

def get_llm(model: str | None = None,temperature: float | None = None):
    """
    Return a configured ChatOllama instance.
    """

    return ChatOllama(
        model=model or DEFAULT_MODEL,
        base_url=DEFAULT_BASE_URL,
        temperature=(
            DEFAULT_TEMPERATURE
            if temperature is None
            else temperature
        ),
    )

class LLMManager:
    """
    Convenience wrapper around ChatOllama.

    Every LLM agent can share the same
    instance of this class.
    """

    def __init__(self,model: str | None = None,temperature: float | None = None):

        self.llm = get_llm(model=model,temperature=temperature)

    def invoke(self,prompt: str | list[BaseMessage]) -> str:

        response = self.llm.invoke(prompt)

        return response.content

    async def ainvoke(self,prompt: str) -> str:
        """
        Async version.
        """

        response = await self.llm.ainvoke(
            prompt
        )

        return response.content

    @property
    def model_name(self) -> str:
        return self.llm.model

    def __repr__(self):

        return (
            f"LLMManager("
            f"model='{self.model_name}')"
        )