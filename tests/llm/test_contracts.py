import pytest
from pydantic import ValidationError

from app.llm.contracts import LLMInterpretation


def test_llm_interpretation_accepts_valid_data() -> None:
    result = LLMInterpretation(
        summary="Revenue declined.",
        facts=[
            "Revenue fell by 28%.",
        ],
        inferences=[
            "South may deserve investigation.",
        ],
        unknowns=[
            "Causality is not established.",
        ],
        recommended_investigations=[
            "Review South order volume.",
        ],
    )

    assert result.summary == "Revenue declined."


def test_llm_interpretation_uses_empty_lists_by_default() -> None:
    result = LLMInterpretation(summary="Revenue declined.")

    assert result.facts == []
    assert result.inferences == []
    assert result.unknowns == []
    assert result.recommended_investigations == []


def test_llm_interpretation_rejects_empty_summary() -> None:
    with pytest.raises(
        ValidationError,
    ):
        LLMInterpretation(
            summary="",
        )


def test_llm_interpretation_rejects_whitespace_summary() -> None:
    with pytest.raises(
        ValidationError,
    ):
        LLMInterpretation(
            summary="   ",
        )


def test_llm_interpretation_strips_summary_whitespace() -> None:
    result = LLMInterpretation(
        summary="  Revenue declined.  ",
    )

    assert result.summary == "Revenue declined."


def test_llm_interpretation_removes_empty_list_items() -> None:
    result = LLMInterpretation(
        summary="Revenue declined.",
        facts=[
            "Revenue fell.",
            "",
            "   ",
        ],
    )

    assert result.facts == [
        "Revenue fell.",
    ]


def test_llm_interpretation_strips_list_item_whitespace() -> None:
    result = LLMInterpretation(
        summary="Revenue declined.",
        facts=[
            "  Revenue fell.  ",
        ],
    )

    assert result.facts == [
        "Revenue fell.",
    ]


def test_llm_interpretation_removes_duplicate_items() -> None:
    result = LLMInterpretation(
        summary="Revenue declined.",
        facts=[
            "Revenue fell.",
            "Revenue fell.",
        ],
    )

    assert result.facts == [
        "Revenue fell.",
    ]
