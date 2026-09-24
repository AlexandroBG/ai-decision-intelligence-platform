from app.evaluation.provider import (
    classify_provider_error,
)
from app.llm.errors import (
    LLMProviderError,
)


def build_provider_error(
    cause_message: str,
) -> LLMProviderError:
    try:
        raise RuntimeError(cause_message)
    except RuntimeError as cause:
        try:
            raise LLMProviderError("Gemini request failed.") from cause
        except LLMProviderError as exc:
            return exc


def test_classifies_resource_exhausted() -> None:
    error = build_provider_error("429 RESOURCE_EXHAUSTED: Quota exceeded.")

    assert classify_provider_error(exc=error) == "rate_or_quota_limit"


def test_classifies_rate_limit() -> None:
    error = build_provider_error("Rate limit reached.")

    assert classify_provider_error(exc=error) == "rate_or_quota_limit"


def test_classifies_generic_provider_error() -> None:
    error = build_provider_error("Unexpected upstream failure.")

    assert classify_provider_error(exc=error) == "provider_error"
