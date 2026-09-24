import pytest

from app.evaluation.case_registry import (
    get_evaluation_case_config,
    list_evaluation_cases,
)


def test_lists_available_evaluation_cases() -> None:
    assert list_evaluation_cases() == (
        "revenue_decline_v1",
        "revenue_comparison_only_v1",
    )


def test_decline_case_requires_recommendation() -> None:
    config = get_evaluation_case_config("revenue_decline_v1")

    assert config.case.case_id == "revenue_decline_v1"

    assert config.require_recommendation is True


def test_comparison_case_does_not_require_recommendation() -> None:
    config = get_evaluation_case_config("revenue_comparison_only_v1")

    assert config.case.case_id == "revenue_comparison_only_v1"

    assert config.require_recommendation is False


def test_registry_rejects_unknown_case() -> None:
    with pytest.raises(
        ValueError,
        match="Unknown evaluation case",
    ):
        get_evaluation_case_config("does_not_exist")
