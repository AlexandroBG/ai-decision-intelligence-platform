import httpx
from google import genai
from google.genai import errors, types

from app.llm.config import LLMConfig
from app.llm.contracts import LLMInterpretation
from app.llm.errors import (
    LLMInputError,
    LLMProviderError,
    LLMResponseError,
)


class GeminiClient:
    def __init__(
        self,
        config: LLMConfig,
    ) -> None:
        self._config = config

        self._client = genai.Client(
            api_key=config.api_key,
        )

    def generate_text(
        self,
        prompt: str,
    ) -> str:
        self._validate_prompt(
            prompt=prompt,
        )

        try:
            response = self._client.models.generate_content(
                model=self._config.model_name,
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

    def generate_interpretation(
        self,
        prompt: str,
    ) -> LLMInterpretation:
        self._validate_prompt(
            prompt=prompt,
        )

        try:
            response = self._client.models.generate_content(
                model=self._config.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=LLMInterpretation,
                ),
            )
        except (
            errors.APIError,
            httpx.HTTPError,
        ) as exc:
            raise LLMProviderError("Gemini request failed.") from exc

        if response.parsed is None:
            raise LLMResponseError("Gemini returned an invalid structured response.")

        return LLMInterpretation.model_validate(response.parsed)

    @staticmethod
    def _validate_prompt(
        prompt: str,
    ) -> None:
        if not prompt.strip():
            raise LLMInputError("Prompt must not be empty.")
