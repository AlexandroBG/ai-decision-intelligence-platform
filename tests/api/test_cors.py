import pytest
from fastapi.testclient import TestClient

from app.api.main import (
    ALLOWED_ORIGINS_ENV,
    DEFAULT_ALLOWED_ORIGINS,
    app,
    load_allowed_origins,
)


@pytest.fixture(autouse=True)
def clear_allowed_origins_environment(
    monkeypatch,
) -> None:
    monkeypatch.delenv(
        ALLOWED_ORIGINS_ENV,
        raising=False,
    )


def test_load_allowed_origins_uses_defaults_when_not_configured() -> None:
    result = load_allowed_origins()

    assert result == DEFAULT_ALLOWED_ORIGINS

    assert result is not DEFAULT_ALLOWED_ORIGINS


def test_load_allowed_origins_uses_environment_configuration(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        ALLOWED_ORIGINS_ENV,
        ("https://decisionai.example.com,https://dashboard.example.com"),
    )

    result = load_allowed_origins()

    assert result == [
        "https://decisionai.example.com",
        "https://dashboard.example.com",
    ]


def test_load_allowed_origins_normalizes_whitespace_and_empty_values(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        ALLOWED_ORIGINS_ENV,
        (" https://decisionai.example.com , , https://dashboard.example.com , "),
    )

    result = load_allowed_origins()

    assert result == [
        "https://decisionai.example.com",
        "https://dashboard.example.com",
    ]


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
