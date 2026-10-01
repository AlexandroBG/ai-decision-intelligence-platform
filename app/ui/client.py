import os
from typing import Any

import httpx
from pydantic import ValidationError

from app.api.contracts import (
    DecisionResponse,
    HealthResponse,
)

DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"

API_BASE_URL_ENV = "DECISIONAI_API_BASE_URL"


class DecisionAPIError(Exception):
    """Base exception for DecisionAI API client failures."""


class DecisionAPIUnavailableError(DecisionAPIError):
    """Raised when the DecisionAI API cannot be reached."""


class DecisionAPITimeoutError(DecisionAPIError):
    """Raised when the DecisionAI API takes too long to respond."""


class DecisionProviderUnavailableError(DecisionAPIError):
    """Raised when the external AI provider is unavailable."""


class DecisionAPIResponseError(DecisionAPIError):
    """Raised when the API returns an invalid response."""


class DecisionAPIHTTPError(DecisionAPIError):
    def __init__(
        self,
        status_code: int,
    ) -> None:
        self.status_code = status_code

        super().__init__(f"DecisionAI API request failed with status {status_code}.")


class DecisionAPIClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        resolved_base_url = base_url or os.getenv(
            API_BASE_URL_ENV,
            DEFAULT_API_BASE_URL,
        )

        self._base_url = resolved_base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    def health(self) -> HealthResponse:
        payload = self._request_json(
            method="GET",
            path="/health",
        )

        try:
            return HealthResponse.model_validate(payload)
        except ValidationError as exc:
            raise DecisionAPIResponseError(
                "DecisionAI API returned an invalid health response."
            ) from exc

    def create_decision(
        self,
        question: str,
    ) -> DecisionResponse:
        payload = self._request_json(
            method="POST",
            path="/decisions",
            json={
                "question": question,
            },
        )

        try:
            return DecisionResponse.model_validate(payload)
        except ValidationError as exc:
            raise DecisionAPIResponseError(
                "DecisionAI API returned an invalid decision response."
            ) from exc

    def _request_json(
        self,
        method: str,
        path: str,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        try:
            response = httpx.request(
                method=method,
                url=f"{self._base_url}{path}",
                json=json,
                timeout=self._timeout_seconds,
            )
        except httpx.TimeoutException as exc:
            raise DecisionAPITimeoutError("DecisionAI API request timed out.") from exc
        except httpx.RequestError as exc:
            raise DecisionAPIUnavailableError(
                "Could not connect to the DecisionAI API."
            ) from exc

        if response.status_code == 503:
            raise DecisionProviderUnavailableError(
                "AI provider is temporarily unavailable."
            )

        if not response.is_success:
            raise DecisionAPIHTTPError(status_code=response.status_code)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DecisionAPIResponseError(
                "DecisionAI API returned invalid JSON."
            ) from exc

        if not isinstance(
            payload,
            dict,
        ):
            raise DecisionAPIResponseError(
                "DecisionAI API returned an unexpected response."
            )

        return payload
