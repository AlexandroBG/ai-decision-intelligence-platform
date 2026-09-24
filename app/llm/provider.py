import os
from typing import Literal

LLMProviderName = Literal[
    "gemini",
    "openai",
]


class LLMProviderConfigurationError(Exception):
    """Raised when the configured LLM provider is invalid."""


def load_llm_provider() -> LLMProviderName:
    provider = (
        os.getenv(
            "LLM_PROVIDER",
            "gemini",
        )
        .strip()
        .lower()
    )

    if provider == "gemini":
        return "gemini"

    if provider == "openai":
        return "openai"

    raise LLMProviderConfigurationError(
        "LLM_PROVIDER must be either 'gemini' or 'openai'."
    )
