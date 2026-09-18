import pytest

from app.llm.config import (
    LLMConfigurationError,
    load_llm_config,
)


def test_load_llm_config_reads_environment(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-key",
    )

    monkeypatch.setenv(
        "GEMINI_MODEL",
        "test-model",
    )

    config = load_llm_config()

    assert config.api_key == "test-key"
    assert config.model_name == "test-model"


def test_load_llm_config_uses_default_model(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_API_KEY",
        "test-key",
    )

    monkeypatch.delenv(
        "GEMINI_MODEL",
        raising=False,
    )

    config = load_llm_config()

    assert config.model_name == "gemini-2.5-flash"


def test_load_llm_config_rejects_missing_api_key(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        "GEMINI_API_KEY",
        raising=False,
    )

    with pytest.raises(
        LLMConfigurationError,
        match="GEMINI_API_KEY",
    ):
        load_llm_config()
