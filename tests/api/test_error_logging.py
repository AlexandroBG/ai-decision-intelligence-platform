import logging

from fastapi.testclient import TestClient

from app.api.contracts import (
    DecisionRequest,
)
from app.api.main import (
    REQUEST_ID_HEADER,
    app,
    get_decision_service,
)
from app.llm.errors import (
    LLMProviderError,
)


class FailingProviderDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ):
        raise LLMProviderError("Gemini request failed.")


def test_provider_failure_logs_request_id(
    caplog,
) -> None:
    app.dependency_overrides[get_decision_service] = lambda: (
        FailingProviderDecisionService()
    )

    try:
        client = TestClient(app)

        with caplog.at_level(
            logging.ERROR,
            logger="decisionai",
        ):
            response = client.post(
                "/decisions",
                json={"question": ("What happened?")},
            )

        assert response.status_code == 503

        request_id = response.headers[REQUEST_ID_HEADER]

        matching_records = [
            record
            for record in caplog.records
            if (
                record.name == "decisionai"
                and "event=provider_error" in record.getMessage()
            )
        ]

        assert len(matching_records) == 1

        message = matching_records[0].getMessage()

        assert f"request_id={request_id}" in message

        assert "event=provider_error" in message

        assert "status_code=503" in message
    finally:
        app.dependency_overrides.clear()
