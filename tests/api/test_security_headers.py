from fastapi.testclient import TestClient

from app.api.main import app


def test_health_includes_security_headers() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert response.headers["X-Frame-Options"] == "DENY"

    assert response.headers["Referrer-Policy"] == "no-referrer"


def test_openapi_includes_security_headers() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    assert response.status_code == 200

    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert response.headers["X-Frame-Options"] == "DENY"

    assert response.headers["Referrer-Policy"] == "no-referrer"
