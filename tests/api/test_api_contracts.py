import pytest
from pydantic import ValidationError

from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
    HealthResponse,
)


def test_decision_request_accepts_valid_question() -> None:
    request = DecisionRequest(question="What happened to revenue?")

    assert request.question == "What happened to revenue?"


def test_decision_request_accepts_maximum_length_question() -> None:
    question = "a" * 2000

    request = DecisionRequest(question=question)

    assert request.question == question

    assert len(request.question) == 2000


def test_decision_request_rejects_empty_question() -> None:
    with pytest.raises(ValidationError):
        DecisionRequest(question="")


def test_decision_request_rejects_question_over_maximum_length() -> None:
    with pytest.raises(ValidationError):
        DecisionRequest(question="a" * 2001)


def test_decision_request_rejects_extra_fields() -> None:
    with pytest.raises(ValidationError):
        DecisionRequest(
            question="What happened?",
            unexpected="value",
        )


def test_decision_response_accepts_completed_result() -> None:
    response = DecisionResponse(
        status="completed",
        answer="Revenue decreased.",
        steps_used=3,
        tool_calls=2,
        evidence_steps=[
            1,
            2,
        ],
    )

    assert response.status == "completed"

    assert response.answer == "Revenue decreased."

    assert response.steps_used == 3

    assert response.tool_calls == 2

    assert response.evidence_steps == [
        1,
        2,
    ]


def test_decision_response_accepts_failed_result() -> None:
    response = DecisionResponse(
        status="failed",
        answer=None,
        steps_used=5,
        tool_calls=3,
        evidence_steps=[],
    )

    assert response.status == "failed"

    assert response.answer is None


def test_decision_response_rejects_negative_steps() -> None:
    with pytest.raises(ValidationError):
        DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=-1,
            tool_calls=0,
            evidence_steps=[],
        )


def test_decision_response_rejects_negative_tool_calls() -> None:
    with pytest.raises(ValidationError):
        DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=1,
            tool_calls=-1,
            evidence_steps=[],
        )


def test_health_response_accepts_valid_payload() -> None:
    response = HealthResponse(
        status="ok",
        service="decisionai-api",
        version="0.1.0",
    )

    assert response.status == "ok"

    assert response.service == "decisionai-api"

    assert response.version == "0.1.0"
