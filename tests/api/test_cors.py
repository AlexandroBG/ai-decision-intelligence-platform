from fastapi.testclient import TestClient

from app.api.main import app


def test_cors_allows_localhost_streamlit_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/decisions",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200

    assert response.headers["access-control-allow-origin"] == "http://localhost:8501"

    assert "POST" in response.headers["access-control-allow-methods"]


def test_cors_allows_loopback_streamlit_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/decisions",
        headers={
            "Origin": "http://127.0.0.1:8501",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 200

    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:8501"


def test_cors_rejects_unknown_origin() -> None:
    client = TestClient(app)

    response = client.options(
        "/decisions",
        headers={
            "Origin": "https://example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )

    assert response.status_code == 400

    assert "access-control-allow-origin" not in response.headers


def test_cors_does_not_allow_arbitrary_methods() -> None:
    client = TestClient(app)

    response = client.options(
        "/decisions",
        headers={
            "Origin": "http://localhost:8501",
            "Access-Control-Request-Method": "DELETE",
        },
    )

    assert response.status_code == 400
