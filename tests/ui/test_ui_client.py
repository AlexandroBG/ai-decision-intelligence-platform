import httpx
import pytest

from app.ui.client import (
    DecisionAPIClient,
    DecisionAPIHTTPError,
    DecisionAPIResponseError,
    DecisionAPITimeoutError,
    DecisionAPIUnavailableError,
    DecisionProviderUnavailableError,
)


def test_health_maps_api_response(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            json={
                "status": "ok",
                "service": "decisionai-api",
                "version": "0.1.0",
            },
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    result = client.health()

    assert result.status == "ok"
    assert result.service == "decisionai-api"
    assert result.version == "0.1.0"


def test_create_decision_maps_api_response(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            json={
                "status": "completed",
                "answer": "Revenue decreased by 28.06%.",
                "steps_used": 3,
                "tool_calls": 2,
                "evidence_steps": [
                    1,
                    2,
                ],
            },
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    result = client.create_decision(question="What happened to revenue?")

    assert result.status == "completed"
    assert result.answer == "Revenue decreased by 28.06%."
    assert result.steps_used == 3
    assert result.tool_calls == 2
    assert result.evidence_steps == [
        1,
        2,
    ]


def test_create_decision_sends_question(
    monkeypatch,
) -> None:
    captured: dict[
        str,
        object,
    ] = {}

    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        captured.update(kwargs)

        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            json={
                "status": "completed",
                "answer": "Result.",
                "steps_used": 1,
                "tool_calls": 0,
                "evidence_steps": [],
            },
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    client.create_decision(question="What happened?")

    assert captured["method"] == "POST"

    assert captured["url"] == "http://127.0.0.1:8000/decisions"

    assert captured["json"] == {
        "question": "What happened?",
    }


def test_client_uses_configured_timeout(
    monkeypatch,
) -> None:
    captured: dict[
        str,
        object,
    ] = {}

    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        captured.update(kwargs)

        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            json={
                "status": "ok",
                "service": "decisionai-api",
                "version": "0.1.0",
            },
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient(timeout_seconds=12.5)

    client.health()

    assert captured["timeout"] == 12.5


def test_client_raises_provider_unavailable_for_503(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=503,
            json={"detail": ("AI provider is temporarily unavailable.")},
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionProviderUnavailableError,
        match="temporarily unavailable",
    ):
        client.create_decision(question="What happened?")


def test_client_raises_timeout_error(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        raise httpx.ReadTimeout(
            "Request timed out",
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionAPITimeoutError,
        match="timed out",
    ):
        client.create_decision(question="What happened?")


def test_client_raises_http_error_for_other_http_failure(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=500,
            json={"detail": ("Internal server error")},
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionAPIHTTPError,
        match="status 500",
    ) as exc_info:
        client.create_decision(question="What happened?")

    assert exc_info.value.status_code == 500


def test_client_raises_when_api_is_unreachable(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        raise httpx.ConnectError(
            "Connection refused",
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionAPIUnavailableError,
        match="Could not connect",
    ):
        client.health()


def test_client_rejects_invalid_decision_contract(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            json={
                "something": "unexpected",
            },
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionAPIResponseError,
        match="invalid decision response",
    ):
        client.create_decision(question="What happened?")


def test_client_rejects_invalid_json(
    monkeypatch,
) -> None:
    def fake_request(
        **kwargs,
    ) -> httpx.Response:
        request = httpx.Request(
            method=kwargs["method"],
            url=kwargs["url"],
        )

        return httpx.Response(
            status_code=200,
            content=b"not-json",
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionAPIResponseError,
        match="invalid JSON",
    ):
        client.health()
