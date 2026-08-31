"""
Centralized Ollama LLM configuration.
All agents should obtain their LLM instance
through this module instead of creating
their own model.
"""

from __future__ import annotations

import os
import time

from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage

DEFAULT_MODEL = os.getenv("OLLAMA_MODEL","gemma4:31b-cloud ")
DEFAULT_BASE_URL = os.getenv("OLLAMA_BASE_URL","http://localhost:11434")
DEFAULT_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE","0.0"))
DEFAULT_TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1.0


class OllamaConnectionError(RuntimeError):
    """Raised when Ollama is unreachable or fails repeatedly."""


def _format_ollama_error(exc: Exception) -> str:
    base_url = DEFAULT_BASE_URL
    return (
        "Ollama is currently unavailable. "
        "If the service is running, try again in a moment."
    )


def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
):
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
        client_kwargs={"timeout": timeout_seconds},
        num_gpu=-1,
    )

class LLMManager:
    """
    Convenience wrapper around ChatOllama.

    Every LLM agent can share the same
    instance of this class.
    """

    def __init__(
        self,
        model: str | None = None,
        temperature: float | None = None,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_retries: int = MAX_RETRIES,
    ):

        self.llm = get_llm(
            model=model,
            temperature=temperature,
            timeout_seconds=timeout_seconds,
        )
        self.max_retries = max_retries

    def invoke(self, prompt: str | list[BaseMessage]) -> str:
        if isinstance(prompt, str):
            prompt_text = prompt
        elif isinstance(prompt, list):
            prompt_text = "\n".join([f"[{getattr(m, 'type', 'message')}] {getattr(m, 'content', str(m))}" for m in prompt])
        else:
            prompt_text = str(prompt)

        print("\n" + "=" * 70, flush=True)
        print(f"[LLM INVOCATION] Model: {self.model_name}", flush=True)
        print(f"[LLM INVOCATION] Prompt length: {len(prompt_text)} characters", flush=True)
        print("-" * 70, flush=True)
        print("[REAL-TIME PROMPT SENT TO LLM]:", flush=True)
        print(prompt_text, flush=True)
        print("-" * 70, flush=True)
        print("[LLM] Starting invocation...", flush=True)

        for attempt in range(self.max_retries + 1):
            start_time = time.perf_counter()

            try:
                response = self.llm.invoke(prompt)
                elapsed = time.perf_counter() - start_time
                content = response.content

                print(
                    f"[LLM] Completed in {elapsed:.2f} seconds",
                    flush=True,
                )
                print(
                    f"[LLM] Response length: {len(content)} characters",
                    flush=True,
                )
                print("[LLM] Response:", flush=True)
                print(content, flush=True)
                print("=" * 70 + "\n", flush=True)

                return content

            except Exception as exc:
                elapsed = time.perf_counter() - start_time
                retries_remaining = self.max_retries - attempt

                print(
                    f"[LLM] Attempt {attempt + 1} failed after {elapsed:.2f} seconds: "
                    f"{type(exc).__name__}: {exc}",
                    flush=True,
                )

                if retries_remaining == 0:
                    print("[LLM] No retries remaining.", flush=True)
                    raise OllamaConnectionError(_format_ollama_error(exc)) from exc

                delay = RETRY_DELAY_SECONDS * (attempt + 1)
                print(
                    f"[LLM] Retrying in {delay:.1f} seconds "
                    f"({retries_remaining} retries remaining)...",
                    flush=True,
                )
                time.sleep(delay)

        raise OllamaConnectionError(
            "Ollama is currently unavailable. Please check that the Ollama service is running and try again."
        )

    async def ainvoke(self, prompt: str | list[BaseMessage]) -> str:
        """
        Async version.
        """
        if isinstance(prompt, str):
            prompt_text = prompt
        elif isinstance(prompt, list):
            prompt_text = "\n".join([f"[{getattr(m, 'type', 'message')}] {getattr(m, 'content', str(m))}" for m in prompt])
        else:
            prompt_text = str(prompt)

        print("\n" + "=" * 70, flush=True)
        print(f"[LLM ASYNC INVOCATION] Model: {self.model_name}", flush=True)
        print(f"[LLM ASYNC INVOCATION] Prompt length: {len(prompt_text)} characters", flush=True)
        print("-" * 70, flush=True)
        print("[REAL-TIME PROMPT SENT TO LLM]:", flush=True)
        print(prompt_text, flush=True)
        print("-" * 70, flush=True)

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