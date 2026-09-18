class LLMError(Exception):
    """Base exception for LLM layer errors."""


class LLMInputError(LLMError):
    """Raised when LLM input is invalid."""


class LLMProviderError(LLMError):
    """Raised when the external LLM provider request fails."""


class LLMResponseError(LLMError):
    """Raised when the LLM provider returns an unusable response."""
