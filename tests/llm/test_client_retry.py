from unittest.mock import MagicMock, patch

import httpx
import pytest
from google.genai import errors
from pydantic import BaseModel

from app.llm.client import (
    MAX_PROVIDER_ATTEMPTS,
    GeminiClient,
)
from app.llm.config import LLMConfig
from app.llm.errors import (
    LLMProviderError,
    LLMRateLimitError,
)


class ExampleStructuredResponse(BaseModel):
    answer: str


class FakeServerError(errors.APIError):
    def __init__(
        self,
        status_code: int,
    ) -> None:
        Exception.__init__(
            self,
            f"Provider error {status_code}",
        )

        self.code = status_code


def build_config() -> LLMConfig:
    return LLMConfig(
        api_key="test-key",
        model_name="test-model",
    )


def test_generate_text_retries_transient_api_error() -> None:
    mock_response = MagicMock()
    mock_response.text = "Recovered response."

    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = [
            FakeServerError(503),
            mock_response,
        ]

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        result = client.generate_text("Explain revenue.")

    assert result == "Recovered response."

    assert mock_client.models.generate_content.call_count == 2

    mock_sleep.assert_called_once_with(0.5)


def test_generate_structured_retries_transient_api_error() -> None:
    mock_response = MagicMock()

    mock_response.parsed = {
        "answer": "Recovered structured response.",
    }

    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = [
            FakeServerError(503),
            mock_response,
        ]

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        result = client.generate_structured(
            prompt="Return structured data.",
            response_model=(ExampleStructuredResponse),
        )

    assert isinstance(
        result,
        ExampleStructuredResponse,
    )

    assert result.answer == "Recovered structured response."

    assert mock_client.models.generate_content.call_count == 2

    mock_sleep.assert_called_once_with(0.5)


def test_generate_structured_stops_after_retry_limit() -> None:
    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = FakeServerError(503)

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        with pytest.raises(
            LLMProviderError,
            match="Gemini request failed",
        ):
            client.generate_structured(
                prompt="Return structured data.",
                response_model=(ExampleStructuredResponse),
            )

    assert mock_client.models.generate_content.call_count == MAX_PROVIDER_ATTEMPTS

    assert mock_sleep.call_count == 2

    assert [call.args[0] for call in mock_sleep.call_args_list] == [
        0.5,
        1.0,
    ]


def test_generate_text_does_not_retry_client_error() -> None:
    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
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

        client = GeminiClient(config=build_config())

        with pytest.raises(
            LLMProviderError,
            match="Gemini request failed",
        ):
            client.generate_text("Explain revenue.")

    assert mock_client.models.generate_content.call_count == 1

    mock_sleep.assert_not_called()


def test_generate_text_retries_timeout() -> None:
    mock_response = MagicMock()
    mock_response.text = "Recovered after timeout."

    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = [
            httpx.ReadTimeout("Temporary timeout."),
            mock_response,
        ]

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        result = client.generate_text("Explain revenue.")

    assert result == "Recovered after timeout."

    assert mock_client.models.generate_content.call_count == 2

    mock_sleep.assert_called_once_with(0.5)


def test_generate_text_does_not_retry_rate_limit() -> None:
    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = FakeServerError(429)

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        with pytest.raises(
            LLMRateLimitError,
            match=("Gemini rate or quota limit reached"),
        ):
            client.generate_text("Explain revenue.")

    assert mock_client.models.generate_content.call_count == 1

    mock_sleep.assert_not_called()


def test_generate_structured_converts_rate_limit() -> None:
    with (
        patch("app.llm.client.genai.Client") as mock_client_class,
        patch("app.llm.client.time.sleep") as mock_sleep,
    ):
        mock_client = MagicMock()

        mock_client.models.generate_content.side_effect = FakeServerError(429)

        mock_client_class.return_value = mock_client

        client = GeminiClient(config=build_config())

        with pytest.raises(
            LLMRateLimitError,
            match=("Gemini rate or quota limit reached"),
        ):
            client.generate_structured(
                prompt="Return structured data.",
                response_model=(ExampleStructuredResponse),
            )

    assert mock_client.models.generate_content.call_count == 1

    mock_sleep.assert_not_called()
