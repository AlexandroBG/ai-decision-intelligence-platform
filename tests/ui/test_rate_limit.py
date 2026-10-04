import httpx
import pytest

from app.ui.client import (
    DecisionAPIClient,
    DecisionProviderRateLimitError,
)


def test_client_raises_provider_rate_limit_for_429(
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
            status_code=429,
            json={"detail": ("AI provider quota or rate limit has been reached.")},
            request=request,
        )

    monkeypatch.setattr(
        httpx,
        "request",
        fake_request,
    )

    client = DecisionAPIClient()

    with pytest.raises(
        DecisionProviderRateLimitError,
        match="quota or rate limit",
    ):
        client.create_decision(question="What happened?")
