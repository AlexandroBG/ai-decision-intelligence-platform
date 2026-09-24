import pytest

from app.llm.provider import (
    LLMProviderConfigurationError,
    load_llm_provider,
)


def test_load_llm_provider_defaults_to_gemini(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "LLM_PROVIDER",
        raising=False,
    )

    provider = load_llm_provider()

    assert provider == "gemini"


def test_load_llm_provider_returns_gemini(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "gemini",
    )

    provider = load_llm_provider()

    assert provider == "gemini"


def test_load_llm_provider_returns_openai(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "openai",
    )

    provider = load_llm_provider()

    assert provider == "openai"


def test_load_llm_provider_rejects_invalid_provider(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "LLM_PROVIDER",
        "invalid-provider",
    )

    with pytest.raises(
        LLMProviderConfigurationError,
        match="LLM_PROVIDER must be either 'gemini' or 'openai'",
    ):
        load_llm_provider()
