import json
from typing import TypeVar

import httpx
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ValidationError

from app.llm.config import LLMConfig
from app.llm.contracts import LLMInterpretation
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)

StructuredResponseT = TypeVar(
    "StructuredResponseT",
    bound=BaseModel,
)


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

        try:
            response = self._client.models.generate_content(
                model=(self._config.model_name),
                contents=prompt,
            )
        except (
            errors.APIError,
            httpx.HTTPError,
        ) as exc:
            raise LLMProviderError("Gemini request failed.") from exc

        if not response.text:
            raise LLMResponseError("Gemini returned an empty response.")

        return response.text

    def generate_structured(
        self,
        prompt: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        self._validate_prompt(prompt=prompt)

        response_schema = response_model.model_json_schema()

        try:
            response = self._client.models.generate_content(
                model=(self._config.model_name),
                contents=prompt,
                config=(
                    types.GenerateContentConfig(
                        response_mime_type=("application/json"),
                        response_json_schema=(response_schema),
                    )
                ),
            )
        except (
            errors.APIError,
            httpx.HTTPError,
        ) as exc:
            raise LLMProviderError("Gemini request failed.") from exc

        if response.parsed is not None:
            return self._validate_parsed_response(
                parsed=response.parsed,
                response_model=response_model,
            )

        if response.text:
            return self._validate_text_response(
                text=response.text,
                response_model=response_model,
            )

        raise LLMResponseError("Gemini returned an empty structured response.")

    def generate_interpretation(
        self,
        prompt: str,
    ) -> LLMInterpretation:
        return self.generate_structured(
            prompt=prompt,
            response_model=(LLMInterpretation),
        )

    @staticmethod
    def _validate_parsed_response(
        parsed: object,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        try:
            return response_model.model_validate(parsed)
        except ValidationError as exc:
            details = GeminiClient._format_validation_error(exc=exc)

            raise LLMResponseError(
                "Gemini returned an invalid "
                "structured response. "
                f"Validation details: {details}"
            ) from exc

    @staticmethod
    def _validate_text_response(
        text: str,
        response_model: type[StructuredResponseT],
    ) -> StructuredResponseT:
        try:
            return response_model.model_validate_json(text)
        except ValidationError as exc:
            details = GeminiClient._format_validation_error(exc=exc)

            raise LLMResponseError(
                "Gemini returned an invalid "
                "structured response: the returned "
                "JSON does not satisfy the requested "
                "contract. "
                f"Validation details: {details}"
            ) from exc

    @staticmethod
    def _format_validation_error(
        exc: ValidationError,
    ) -> str:
        simplified_errors = []

        for error in exc.errors(
            include_url=False,
            include_context=False,
            include_input=False,
        ):
            simplified_errors.append(
                {
                    "type": error.get("type"),
                    "loc": list(
                        error.get(
                            "loc",
                            (),
                        )
                    ),
                    "msg": error.get("msg"),
                }
            )

        return json.dumps(
            simplified_errors,
            ensure_ascii=False,
            default=str,
        )

    @staticmethod
    def _validate_prompt(
        prompt: str,
    ) -> None:
        if not prompt.strip():
            raise LLMInputError("Prompt must not be empty.")
