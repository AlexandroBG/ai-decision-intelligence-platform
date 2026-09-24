import pytest

from app.agent.language_policy import (
    OBSERVATIONAL_LANGUAGE_POLICY,
)
from app.agent.prompt_policy import (
    apply_language_policy,
)


def test_apply_language_policy_preserves_original_prompt() -> None:
    original = "You are the DecisionAI agent."

    result = apply_language_policy(prompt=original)

    assert original in result


def test_apply_language_policy_adds_policy() -> None:
    result = apply_language_policy(prompt=("You are the DecisionAI agent."))

    assert OBSERVATIONAL_LANGUAGE_POLICY in result


def test_apply_language_policy_adds_policy_after_prompt() -> None:
    original = "Original prompt."

    result = apply_language_policy(prompt=original)

    assert result.startswith(original)

    assert result.endswith(OBSERVATIONAL_LANGUAGE_POLICY)


def test_apply_language_policy_rejects_empty_prompt() -> None:
    with pytest.raises(
        ValueError,
        match=("Prompt must not be empty"),
    ):
        apply_language_policy(prompt="   ")
