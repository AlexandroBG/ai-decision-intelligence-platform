from typing import Literal

from app.llm.errors import LLMProviderError

ProviderErrorKind = Literal[
    "rate_or_quota_limit",
    "provider_error",
]


def classify_provider_error(
    exc: LLMProviderError,
) -> ProviderErrorKind:
    current: BaseException | None = exc

    while current is not None:
        message = str(current).lower()

        if _looks_like_rate_or_quota_limit(message=message):
            return "rate_or_quota_limit"

        current = current.__cause__

    return "provider_error"


def _looks_like_rate_or_quota_limit(
    message: str,
) -> bool:
    indicators = (
        "resource_exhausted",
        "resource exhausted",
        "quota exceeded",
        "rate limit",
        "429",
    )

    return any(indicator in message for indicator in indicators)
