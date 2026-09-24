import os
from dataclasses import dataclass


class OpenAIConfigurationError(Exception):
    """Raised when OpenAI configuration is missing or invalid."""


@dataclass(frozen=True)
class OpenAIConfig:
    api_key: str
    model_name: str


def load_openai_config() -> OpenAIConfig:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise OpenAIConfigurationError(
            "OPENAI_API_KEY environment variable is not configured."
        )

    model_name = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna",
    )

    return OpenAIConfig(
        api_key=api_key,
        model_name=model_name,
    )
