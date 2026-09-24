from fastapi.testclient import (
    TestClient,
)

from app.api.main import (
    APP_VERSION,
    SERVICE_NAME,
    app,
)

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")

    assert response.status_code == 200


def test_health_returns_expected_payload() -> None:
    response = client.get("/health")

    assert response.json() == {
        "status": "ok",
        "service": (SERVICE_NAME),
        "version": (APP_VERSION),
    }


def test_health_returns_json() -> None:
    response = client.get("/health")

    assert response.headers["content-type"].startswith("application/json")


def test_openapi_document_is_available() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()

    assert schema["info"]["title"] == "DecisionAI API"

    assert schema["info"]["version"] == APP_VERSION


def test_health_is_present_in_openapi() -> None:
    response = client.get("/openapi.json")

    schema = response.json()

    assert "/health" in schema["paths"]
