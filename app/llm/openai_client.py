from typing import TypeVar

import openai
from openai import OpenAI
from pydantic import BaseModel

from app.llm.contracts import LLMInterpretation
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)
from app.llm.openai_config import OpenAIConfig
from app.observability.context import get_request_id
from app.observability.logging import get_logger
from app.observability.metrics import metrics

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)


logger = get_logger()


class OpenAIClient:
    def __init__(
        self,
        config: OpenAIConfig,
    ) -> None:
        self._config = config

        self._client = OpenAI(
            api_key=config.api_key,
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        self._validate_prompt(
            prompt=prompt,
        )

        request_id = get_request_id()

        try:
            response = self._client.responses.create(
                model=self._config.model_name,
                input=prompt,
            )

        except openai.OpenAIError as exc:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_text",
                success=False,
            )

            raise LLMProviderError("OpenAI request failed.") from exc

        response_text = response.output_text

        if not response_text:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_text",
                success=False,
            )

            raise LLMResponseError("OpenAI returned an empty response.")

        self._log_llm_call(
            request_id=request_id,
            operation="generate_text",
            success=True,
        )

        return response_text

    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        self._validate_prompt(
            prompt=prompt,
        )

        request_id = get_request_id()

        try:
            response = self._client.responses.parse(
                model=self._config.model_name,
                input=prompt,
                text_format=response_model,
            )

        except openai.OpenAIError as exc:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_structured",
                success=False,
            )

            raise LLMProviderError("OpenAI request failed.") from exc

        result = response.output_parsed

        if result is None:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_structured",
                success=False,
            )

            raise LLMResponseError("OpenAI returned an invalid structured response.")

        self._log_llm_call(
            request_id=request_id,
            operation="generate_structured",
            success=True,
        )

        return result

    def generate_interpretation(
        self,
        prompt: str,
    ) -> LLMInterpretation:
        return self.generate_structured(
            prompt=prompt,
            response_model=LLMInterpretation,
        )

    @staticmethod
    def _validate_prompt(
        prompt: str,
    ) -> None:
        if not prompt.strip():
            raise LLMInputError("Prompt must not be empty.")

    def _log_llm_call(
        self,
        request_id: str,
        operation: str,
        success: bool,
    ) -> None:
        metrics.increment("llm_calls_total")

        log_method = logger.info if success else logger.error

        log_method(
            ("request_id=%s event=llm_call model=%s operation=%s success=%s"),
            request_id,
            self._config.model_name,
            operation,
            str(success).lower(),
        )
