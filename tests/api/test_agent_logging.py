import logging

from fastapi.testclient import TestClient

from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
)
from app.api.main import (
    REQUEST_ID_HEADER,
    app,
    get_decision_service,
)


class CompletedDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        return DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=3,
            tool_calls=2,
            evidence_steps=[
                1,
                2,
            ],
        )


class FailedDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        return DecisionResponse(
            status="failed",
            answer=None,
            steps_used=5,
            tool_calls=3,
            evidence_steps=[],
        )


def test_completed_agent_run_logs_outcome(
    caplog,
) -> None:
    app.dependency_overrides[get_decision_service] = lambda: CompletedDecisionService()

    try:
        client = TestClient(app)

        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = client.post(
                "/decisions",
                json={"question": ("What happened?")},
            )

        assert response.status_code == 200

        request_id = response.headers[REQUEST_ID_HEADER]

        matching_records = [
            record
            for record in caplog.records
            if (
                record.name == "decisionai"
                and "event=agent_completed" in record.getMessage()
            )
        ]

        assert len(matching_records) == 1

        message = matching_records[0].getMessage()

        assert f"request_id={request_id}" in message

        assert "event=agent_completed" in message

        assert "steps_used=3" in message

        assert "tool_calls=2" in message

        assert "evidence_steps=2" in message
    finally:
        app.dependency_overrides.clear()


def test_failed_agent_run_logs_outcome(
    caplog,
) -> None:
    app.dependency_overrides[get_decision_service] = lambda: FailedDecisionService()

    try:
        client = TestClient(app)

        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = client.post(
                "/decisions",
                json={"question": ("What happened?")},
            )

        assert response.status_code == 200

        request_id = response.headers[REQUEST_ID_HEADER]

        matching_records = [
            record
            for record in caplog.records
            if (
                record.name == "decisionai"
                and "event=agent_failed" in record.getMessage()
            )
        ]

        assert len(matching_records) == 1

        message = matching_records[0].getMessage()

        assert f"request_id={request_id}" in message

        assert "event=agent_failed" in message

        assert "steps_used=5" in message

        assert "tool_calls=3" in message

        assert "evidence_steps=0" in message
    finally:
        app.dependency_overrides.clear()
