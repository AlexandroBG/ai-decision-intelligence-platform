from uuid import UUID

from fastapi.testclient import TestClient

from app.api.main import (
    REQUEST_ID_HEADER,
    app,
)


def test_health_returns_request_id() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200

    request_id = response.headers[REQUEST_ID_HEADER]

    parsed_request_id = UUID(request_id)

    assert str(parsed_request_id) == request_id


def test_request_ids_are_unique() -> None:
    client = TestClient(app)

    first_response = client.get("/health")

    second_response = client.get("/health")

    first_request_id = first_response.headers[REQUEST_ID_HEADER]

    second_request_id = second_response.headers[REQUEST_ID_HEADER]

    assert first_request_id != second_request_id


def test_request_id_is_present_with_security_headers() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert REQUEST_ID_HEADER in response.headers

    assert response.headers["X-Content-Type-Options"] == "nosniff"

    assert response.headers["X-Frame-Options"] == "DENY"

    assert response.headers["Referrer-Policy"] == "no-referrer"
