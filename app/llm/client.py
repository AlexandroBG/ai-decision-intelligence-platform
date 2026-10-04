import time
from typing import NoReturn, TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.llm.config import LLMConfig
from app.llm.contracts import LLMInterpretation
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMRateLimitError,
    LLMResponseError,
)
from app.observability.context import get_request_id
from app.observability.logging import get_logger
from app.observability.metrics import metrics

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)

MAX_PROVIDER_ATTEMPTS = 3

RETRY_DELAYS_SECONDS = (
    0.5,
    1.0,
)

RETRYABLE_PROVIDER_STATUS_CODES = {
    500,
    502,
    503,
    504,
}


logger = get_logger()


class GeminiClient:
    def __init__(
        self,
        config: LLMConfig,
    ) -> None:
        self._config = config

        self._client = genai.Client(api_key=config.api_key)

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        self._validate_prompt(prompt=prompt)

        request_id = get_request_id()

        try:
            response = self._generate_with_retry(
                request_id=request_id,
                operation="generate_text",
                generate=lambda: self._client.models.generate_content(
                    model=self._config.model_name,
                    contents=prompt,
                ),
            )

        except (
            errors.APIError,
            httpx.HTTPError,
        ) as exc:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_text",
                success=False,
            )

            self._raise_provider_error(exc=exc)

        if not response.text:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_text",
                success=False,
            )

            raise LLMResponseError("Gemini returned an empty response.")

        self._log_llm_call(
            request_id=request_id,
            operation="generate_text",
            success=True,
        )

        return response.text

    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        self._validate_prompt(prompt=prompt)

        request_id = get_request_id()

        response_schema = response_model.model_json_schema()

        try:
            response = self._generate_with_retry(
                request_id=request_id,
                operation="generate_structured",
                generate=lambda: self._client.models.generate_content(
                    model=self._config.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type=("application/json"),
                        response_json_schema=(response_schema),
                    ),
                ),
            )

        except (
            errors.APIError,
            httpx.HTTPError,
        ) as exc:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_structured",
                success=False,
            )

            self._raise_provider_error(exc=exc)

        try:
            result = self._parse_structured_response(
                response=response,
                response_model=response_model,
            )

        except LLMResponseError:
            self._log_llm_call(
                request_id=request_id,
                operation="generate_structured",
                success=False,
            )

            raise

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

    def _generate_with_retry(
        self,
        request_id: str,
        operation: str,
        generate,
    ):
        for attempt in range(
            1,
            MAX_PROVIDER_ATTEMPTS + 1,
        ):
            try:
                return generate()

            except (
                errors.APIError,
                httpx.HTTPError,
            ) as exc:
                if (
                    attempt >= MAX_PROVIDER_ATTEMPTS
                    or not self._is_retryable_provider_error(exc=exc)
                ):
                    raise

                delay_seconds = RETRY_DELAYS_SECONDS[attempt - 1]

                logger.warning(
                    (
                        "request_id=%s "
                        "event=llm_retry "
                        "model=%s "
                        "operation=%s "
                        "attempt=%s "
                        "max_attempts=%s "
                        "delay_seconds=%s"
                    ),
                    request_id,
                    self._config.model_name,
                    operation,
                    attempt,
                    MAX_PROVIDER_ATTEMPTS,
                    delay_seconds,
                )

                time.sleep(delay_seconds)

        raise RuntimeError("Provider retry loop exited unexpectedly.")

    @staticmethod
    def _is_retryable_provider_error(
        exc: Exception,
    ) -> bool:
        if isinstance(
            exc,
            errors.APIError,
        ):
            status_code = getattr(
                exc,
                "code",
                None,
            )

            return status_code in RETRYABLE_PROVIDER_STATUS_CODES

        if isinstance(
            exc,
            (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ),
        ):
            return True

        if isinstance(
            exc,
            httpx.HTTPStatusError,
        ):
            return exc.response.status_code in RETRYABLE_PROVIDER_STATUS_CODES

        return False

    @staticmethod
    def _raise_provider_error(
        exc: Exception,
    ) -> NoReturn:
        if (
            isinstance(
                exc,
                errors.APIError,
            )
            and getattr(
                exc,
                "code",
                None,
            )
            == 429
        ):
            raise LLMRateLimitError("Gemini rate or quota limit reached.") from exc

        if (
            isinstance(
                exc,
                httpx.HTTPStatusError,
            )
            and exc.response.status_code == 429
        ):
            raise LLMRateLimitError("Gemini rate or quota limit reached.") from exc

        raise LLMProviderError("Gemini request failed.") from exc

    @staticmethod
    def _parse_structured_response(
        response,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        try:
            if isinstance(
                response.parsed,
                response_model,
            ):
                return response.parsed

            if response.parsed is not None:
                return response_model.model_validate(response.parsed)

            response_text = response.text

            if (
                isinstance(
                    response_text,
                    str,
                )
                and response_text.strip()
            ):
                return response_model.model_validate_json(response_text)

        except (
            ValidationError,
            ValueError,
            TypeError,
        ) as exc:
            raise LLMResponseError(
                "Gemini returned an invalid structured response."
            ) from exc

        raise LLMResponseError("Gemini returned an invalid structured response.")

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
