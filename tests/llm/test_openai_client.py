from unittest.mock import MagicMock, patch

import openai
import pytest
from pydantic import BaseModel

from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)
from app.llm.openai_client import OpenAIClient
from app.llm.openai_config import OpenAIConfig


class ExampleResponse(BaseModel):
    value: str


def build_config() -> OpenAIConfig:
    return OpenAIConfig(
        api_key="test-openai-key",
        model_name="gpt-5.6-luna",
    )


def test_generate_text_returns_response_text() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        sdk_client.responses.create.return_value.output_text = "Hello"

        client = OpenAIClient(
            config=build_config(),
        )

        result = client.generate_text(
            prompt="Say hello.",
        )

        assert result == "Hello"

        sdk_client.responses.create.assert_called_once_with(
            model="gpt-5.6-luna",
            input="Say hello.",
        )


def test_generate_text_rejects_empty_prompt() -> None:
    with patch("app.llm.openai_client.OpenAI"):
        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMInputError,
            match="Prompt must not be empty",
        ):
            client.generate_text("")


def test_generate_text_rejects_whitespace_prompt() -> None:
    with patch("app.llm.openai_client.OpenAI"):
        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMInputError,
            match="Prompt must not be empty",
        ):
            client.generate_text("   ")


def test_generate_text_converts_provider_error() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        sdk_client.responses.create.side_effect = openai.APIError(
            message="Provider failed",
            request=MagicMock(),
            body=None,
        )

        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMProviderError,
            match="OpenAI request failed",
        ):
            client.generate_text(
                prompt="Hello",
            )


def test_generate_text_rejects_empty_response() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        sdk_client.responses.create.return_value.output_text = ""

        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMResponseError,
            match="OpenAI returned an empty response",
        ):
            client.generate_text(
                prompt="Hello",
            )


def test_generate_structured_returns_parsed_model() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        expected = ExampleResponse(
            value="success",
        )

        sdk_client.responses.parse.return_value.output_parsed = expected

        client = OpenAIClient(
            config=build_config(),
        )

        result = client.generate_structured(
            prompt="Return structured data.",
            response_model=ExampleResponse,
        )

        assert result == expected

        sdk_client.responses.parse.assert_called_once_with(
            model="gpt-5.6-luna",
            input="Return structured data.",
            text_format=ExampleResponse,
        )


def test_generate_structured_converts_provider_error() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        sdk_client.responses.parse.side_effect = openai.APIError(
            message="Provider failed",
            request=MagicMock(),
            body=None,
        )

        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMProviderError,
            match="OpenAI request failed",
        ):
            client.generate_structured(
                prompt="Return structured data.",
                response_model=ExampleResponse,
            )


def test_generate_structured_rejects_missing_parsed_output() -> None:
    with patch("app.llm.openai_client.OpenAI") as openai_class:
        sdk_client = MagicMock()
        openai_class.return_value = sdk_client

        sdk_client.responses.parse.return_value.output_parsed = None

        client = OpenAIClient(
            config=build_config(),
        )

        with pytest.raises(
            LLMResponseError,
            match="OpenAI returned an invalid structured response",
        ):
            client.generate_structured(
                prompt="Return structured data.",
                response_model=ExampleResponse,
            )
