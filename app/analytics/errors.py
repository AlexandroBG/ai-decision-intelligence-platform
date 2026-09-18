class AnalyticsError(Exception):
    """Base exception for analytics errors."""


class EmptyAnalyticsInputError(AnalyticsError):
    """Raised when analytics receives an empty input dataset."""


class EmptyPeriodError(AnalyticsError):
    """Raised when a requested analytics period contains no data."""
