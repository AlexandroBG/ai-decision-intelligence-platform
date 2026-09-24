from fastapi.testclient import TestClient

from app.api.main import app
from app.observability.metrics import (
    metrics,
)


def test_metrics_endpoint_returns_counters() -> None:
    metrics.reset()

    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200

    payload = response.json()

    assert payload["requests_total"] == 1

    assert payload["provider_errors_total"] == 0

    assert payload["agent_completed_total"] == 0

    assert payload["agent_failed_total"] == 0

    assert payload["tool_calls_total"] == 0

    assert payload["llm_calls_total"] == 0


def test_health_increments_request_counter() -> None:
    metrics.reset()

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    assert metrics.snapshot()["requests_total"] == 1
