from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    is_valid: bool
    errors: list[str]
