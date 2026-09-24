from app.llm import factory


def test_build_llm_client_builds_gemini_client(
    monkeypatch,
) -> None:
    fake_config = object()
    fake_client = object()

    captured: dict[
        str,
        object,
    ] = {}

    monkeypatch.setattr(
        factory,
        "load_llm_provider",
        lambda: "gemini",
    )

    monkeypatch.setattr(
        factory,
        "load_llm_config",
        lambda: fake_config,
    )

    def fail_openai_config():
        raise AssertionError(
            "OpenAI configuration should not be loaded when Gemini is selected."
        )

    monkeypatch.setattr(
        factory,
        "load_openai_config",
        fail_openai_config,
    )

    def fake_gemini_client(
        config,
    ):
        captured["config"] = config
        return fake_client

    monkeypatch.setattr(
        factory,
        "GeminiClient",
        fake_gemini_client,
    )

    result = factory.build_llm_client()

    assert result is fake_client
    assert captured["config"] is fake_config


def test_build_llm_client_builds_openai_client(
    monkeypatch,
) -> None:
    fake_config = object()
    fake_client = object()

    captured: dict[
        str,
        object,
    ] = {}

    monkeypatch.setattr(
        factory,
        "load_llm_provider",
        lambda: "openai",
    )

    monkeypatch.setattr(
        factory,
        "load_openai_config",
        lambda: fake_config,
    )

    def fail_gemini_config():
        raise AssertionError(
            "Gemini configuration should not be loaded when OpenAI is selected."
        )

    monkeypatch.setattr(
        factory,
        "load_llm_config",
        fail_gemini_config,
    )

    def fake_openai_client(
        config,
    ):
        captured["config"] = config
        return fake_client

    monkeypatch.setattr(
        factory,
        "OpenAIClient",
        fake_openai_client,
    )

    result = factory.build_llm_client()

    assert result is fake_client
    assert captured["config"] is fake_config
