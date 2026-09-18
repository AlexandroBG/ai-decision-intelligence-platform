from unittest.mock import MagicMock, patch

import pytest
from google.genai import errors

from app.llm.client import GeminiClient
from app.llm.config import LLMConfig
from app.llm.contracts import LLMInterpretation
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)


def build_config() -> LLMConfig:
    return LLMConfig(
        api_key="test-key",
        model_name="test-model",
    )


def test_generate_text_returns_response_text() -> None:
    mock_response = MagicMock()
    mock_response.text = "Revenue declined."

    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.return_value = mock_response

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        result = client.generate_text("Explain the revenue decline.")

    assert result == "Revenue declined."


def test_generate_text_rejects_empty_prompt() -> None:
    with patch("app.llm.client.genai.Client"):
        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMInputError,
            match="Prompt must not be empty",
        ):
            client.generate_text("")


def test_generate_text_rejects_whitespace_prompt() -> None:
    with patch("app.llm.client.genai.Client"):
        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMInputError,
            match="Prompt must not be empty",
        ):
            client.generate_text("   ")


def test_generate_text_rejects_empty_response() -> None:
    mock_response = MagicMock()
    mock_response.text = None

    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.return_value = mock_response

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMResponseError,
            match="Gemini returned an empty response",
        ):
            client.generate_text("Explain revenue.")


def test_generate_text_wraps_provider_error() -> None:
    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = errors.ClientError(
            400,
            {
                "error": {
                    "message": "Invalid request",
                }
            },
        )

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMProviderError,
            match="Gemini request failed",
        ):
            client.generate_text("Explain revenue.")


def test_generate_interpretation_returns_contract() -> None:
    mock_response = MagicMock()

    mock_response.parsed = {
        "summary": "Revenue declined.",
        "facts": [
            "Revenue fell by 28%.",
        ],
        "inferences": [
            "South may deserve investigation.",
        ],
        "unknowns": [
            "Causality is not established.",
        ],
        "recommended_investigations": [
            "Review South order volume.",
        ],
    }

    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.return_value = mock_response

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        result = client.generate_interpretation("Interpret the evidence.")

    assert isinstance(
        result,
        LLMInterpretation,
    )

    assert result.summary == "Revenue declined."


def test_generate_interpretation_rejects_empty_prompt() -> None:
    with patch("app.llm.client.genai.Client"):
        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMInputError,
            match="Prompt must not be empty",
        ):
            client.generate_interpretation("")


def test_generate_interpretation_rejects_invalid_response() -> None:
    mock_response = MagicMock()
    mock_response.parsed = None

    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.return_value = mock_response

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMResponseError,
            match="Gemini returned an invalid structured response",
        ):
            client.generate_interpretation("Interpret the evidence.")


def test_generate_interpretation_wraps_provider_error() -> None:
    with patch("app.llm.client.genai.Client") as mock_client_class:
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = errors.ClientError(
            400,
            {
                "error": {
                    "message": "Invalid request",
                }
            },
        )

        mock_client_class.return_value = mock_client

        client = GeminiClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMProviderError,
            match="Gemini request failed",
        ):
            client.generate_interpretation("Interpret the evidence.")
