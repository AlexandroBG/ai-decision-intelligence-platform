from fastapi.testclient import TestClient

from app.api.contracts import (
    DecisionRequest,
)
from app.api.main import (
    app,
    get_decision_service,
)
from app.llm.errors import (
    LLMRateLimitError,
)


class RateLimitedDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ):
        raise LLMRateLimitError("Provider rate or quota limit reached.")


def test_decisions_returns_429_when_provider_rate_limited() -> None:
    app.dependency_overrides[get_decision_service] = lambda: (
        RateLimitedDecisionService()
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={"question": "What happened?"},
        )

        assert response.status_code == 429

        assert response.json() == {
            "detail": ("AI provider quota or rate limit has been reached.")
        }

    finally:
        app.dependency_overrides.clear()
