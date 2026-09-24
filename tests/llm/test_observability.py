import logging
from types import SimpleNamespace

import pytest
from google.genai import errors
from pydantic import BaseModel

from app.llm.client import GeminiClient
from app.llm.config import LLMConfig
from app.llm.errors import (
    LLMProviderError,
)
from app.observability.context import (
    reset_request_id,
    set_request_id,
)


class StructuredResult(BaseModel):
    value: str


def build_client() -> GeminiClient:
    return GeminiClient(
        config=LLMConfig(
            api_key="test-key",
            model_name="gemini-2.5-flash",
        )
    )


def test_generate_structured_logs_success(
    monkeypatch,
    caplog,
) -> None:
    client = build_client()

    def fake_generate_content(
        **kwargs,
    ):
        return SimpleNamespace(
            parsed={
                "value": "ok",
            },
            text=None,
        )

    monkeypatch.setattr(
        client._client.models,
        "generate_content",
        fake_generate_content,
    )

    token = set_request_id("test-request-id")

    try:
        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            result = client.generate_structured(
                prompt="Test prompt",
                response_model=StructuredResult,
            )

        assert result.value == "ok"

        matching_records = [
            record
            for record in caplog.records
            if (record.name == "decisionai" and "event=llm_call" in record.getMessage())
        ]

        assert len(matching_records) == 1

        message = matching_records[0].getMessage()

        assert "request_id=test-request-id" in message

        assert "model=gemini-2.5-flash" in message

        assert "operation=generate_structured" in message

        assert "success=true" in message

    finally:
        reset_request_id(token)


def test_generate_structured_logs_failure(
    monkeypatch,
    caplog,
) -> None:
    client = build_client()

    def fake_generate_content(
        **kwargs,
    ):
        raise errors.APIError(
            500,
            {
                "error": {
                    "message": "provider failure",
                }
            },
            None,
        )

    monkeypatch.setattr(
        client._client.models,
        "generate_content",
        fake_generate_content,
    )

    token = set_request_id("test-request-id")

    try:
        with (
            caplog.at_level(
                logging.ERROR,
                logger="decisionai",
            ),
            pytest.raises(
                LLMProviderError,
                match="Gemini request failed",
            ),
        ):
            client.generate_structured(
                prompt="Test prompt",
                response_model=StructuredResult,
            )

        matching_records = [
            record
            for record in caplog.records
            if (record.name == "decisionai" and "event=llm_call" in record.getMessage())
        ]

        assert len(matching_records) == 1

        message = matching_records[0].getMessage()

        assert "request_id=test-request-id" in message

        assert "model=gemini-2.5-flash" in message

        assert "operation=generate_structured" in message

        assert "success=false" in message

    finally:
        reset_request_id(token)
