class MLError(Exception):
    """Base exception for ML engine errors."""


class MLInputError(MLError):
    """Raised when ML input data or configuration is invalid."""


class MLTrainingError(MLError):
    """Raised when an ML model cannot be trained."""


class MLInferenceError(MLError):
    """Raised when ML inference cannot be completed."""


class MLModelArtifactError(MLError):
    """Raised when a persisted ML model artifact is invalid."""
