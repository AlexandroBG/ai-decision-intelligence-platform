import os
from dataclasses import dataclass


class LLMConfigurationError(Exception):
    """Raised when LLM configuration is missing or invalid."""


@dataclass(frozen=True)
class LLMConfig:
    api_key: str
    model_name: str


def load_llm_config() -> LLMConfig:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise LLMConfigurationError(
            "GEMINI_API_KEY environment variable is not configured."
        )

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash",
    )

    return LLMConfig(
        api_key=api_key,
        model_name=model_name,
    )
