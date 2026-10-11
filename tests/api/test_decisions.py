import pytest
from fastapi.testclient import TestClient

import app.api.main as main_module
from app.agent.contracts import AgentDecision, AgentHistory
from app.agent.loop import AgentLoop
from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
)
from app.api.main import (
    app,
    get_decision_service,
)
from app.api.service import RuntimeDecisionService
from app.llm.errors import (
    LLMProviderError,
)
from app.tools.base import BaseTool
from app.tools.contracts import ToolCall, ToolDefinition, ToolResult
from app.tools.errors import ToolExecutionError
from app.tools.executor import ToolExecutor
from app.tools.registry import ToolRegistry


class FakeDecisionService:
    def __init__(
        self,
        response: DecisionResponse,
    ) -> None:
        self.response = response
        self.requests: list[DecisionRequest] = []

    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        self.requests.append(request)

        return self.response


class FailingProviderDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        raise LLMProviderError("Gemini request failed.")


def test_decisions_returns_fake_service_response() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer=("Revenue decreased by 28.06%."),
            steps_used=3,
            tool_calls=2,
            evidence_steps=[
                1,
                2,
            ],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={"question": ("What is affecting revenue?")},
        )

        assert response.status_code == 200

        assert response.json() == {
            "status": "completed",
            "answer": ("Revenue decreased by 28.06%."),
            "steps_used": 3,
            "tool_calls": 2,
            "evidence_steps": [
                1,
                2,
            ],
        }
    finally:
        app.dependency_overrides.clear()


def test_decisions_passes_request_to_service() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=1,
            tool_calls=0,
            evidence_steps=[],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        client.post(
            "/decisions",
            json={"question": ("What happened?")},
        )

        assert len(fake_service.requests) == 1

        assert fake_service.requests[0].question == "What happened?"
    finally:
        app.dependency_overrides.clear()


def test_decisions_rejects_empty_question() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=1,
            tool_calls=0,
            evidence_steps=[],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={
                "question": "",
            },
        )

        assert response.status_code == 422

        assert fake_service.requests == []
    finally:
        app.dependency_overrides.clear()


def test_decisions_rejects_question_over_maximum_length() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=1,
            tool_calls=0,
            evidence_steps=[],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={
                "question": ("a" * 2001),
            },
        )

        assert response.status_code == 422

        assert fake_service.requests == []
    finally:
        app.dependency_overrides.clear()


def test_decisions_rejects_extra_fields() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer="Result.",
            steps_used=1,
            tool_calls=0,
            evidence_steps=[],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={
                "question": ("What happened?"),
                "unexpected": ("value"),
            },
        )

        assert response.status_code == 422

        assert fake_service.requests == []
    finally:
        app.dependency_overrides.clear()


def test_decisions_uses_runtime_service_by_default(
    monkeypatch,
) -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="completed",
            answer=("Runtime service result."),
            steps_used=2,
            tool_calls=1,
            evidence_steps=[
                1,
            ],
        )
    )

    monkeypatch.setattr(
        main_module,
        "build_runtime_decision_service",
        lambda: fake_service,
    )

    client = TestClient(app)

    response = client.post(
        "/decisions",
        json={"question": ("What happened?")},
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "completed",
        "answer": ("Runtime service result."),
        "steps_used": 2,
        "tool_calls": 1,
        "evidence_steps": [
            1,
        ],
    }

    assert len(fake_service.requests) == 1


def test_decisions_returns_200_for_agent_termination() -> None:
    fake_service = FakeDecisionService(
        response=DecisionResponse(
            status="failed",
            answer=None,
            steps_used=5,
            tool_calls=3,
            evidence_steps=[],
        )
    )

    app.dependency_overrides[get_decision_service] = lambda: fake_service

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={"question": ("What happened?")},
        )

        assert response.status_code == 200

        assert response.json() == {
            "status": "failed",
            "answer": None,
            "steps_used": 5,
            "tool_calls": 3,
            "evidence_steps": [],
        }
    finally:
        app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("exception", "expected_error"),
    [
        pytest.param(
            RuntimeError("PRIVATE_TOOL_EXCEPTION_SENTINEL_123"),
            "Tool execution failed.",
            id="unexpected_exception",
        ),
        pytest.param(
            ToolExecutionError("Expected tool failure."),
            "Expected tool failure.",
            id="expected_domain_failure",
        ),
    ],
)
def test_decisions_handles_tool_implementation_errors(
    monkeypatch,
    exception: Exception,
    expected_error: str,
) -> None:
    class FailingTool(BaseTool):
        @property
        def definition(self) -> ToolDefinition:
            return ToolDefinition(
                name="failing_tool",
                description="Tool used to verify API failure handling.",
            )

        def _run(self, call: ToolCall) -> ToolResult:
            raise exception

    observed_results: list[ToolResult] = []

    def decide(question: str, history: AgentHistory) -> AgentDecision:
        observed_results.extend(
            observation.result for observation in history.observations
        )
        return AgentDecision(
            action={
                "action_type": "tool_call",
                "call": {"tool_name": "failing_tool", "arguments": {}},
            }
        )

    registry = ToolRegistry()
    registry.register(FailingTool())
    loop = AgentLoop(
        executor=ToolExecutor(registry=registry),
        decide=decide,
        max_steps=2,
        max_tool_failures=1,
    )
    service = RuntimeDecisionService(runner=loop)
    monkeypatch.setitem(
        app.dependency_overrides, get_decision_service, lambda: service
    )

    response = TestClient(app).post(
        "/decisions",
        json={"question": "Run the failing tool."},
    )

    assert len(observed_results) == 1
    assert observed_results[0].success is False
    assert observed_results[0].error == expected_error
    assert response.status_code == 200
    assert str(exception) not in response.text
    assert response.json() == {
        "status": "failed",
        "answer": None,
        "steps_used": 2,
        "tool_calls": 1,
        "evidence_steps": [],
    }


def test_decisions_returns_503_when_provider_fails() -> None:
    app.dependency_overrides[get_decision_service] = lambda: (
        FailingProviderDecisionService()
    )

    try:
        client = TestClient(app)

        response = client.post(
            "/decisions",
            json={"question": ("What happened?")},
        )

        assert response.status_code == 503

        assert response.json() == {
            "detail": ("AI provider is temporarily unavailable.")
        }
    finally:
        app.dependency_overrides.clear()


def test_decisions_is_present_in_openapi() -> None:
    client = TestClient(app)

    response = client.get("/openapi.json")

    schema = response.json()

    assert "/decisions" in schema["paths"]

    assert "post" in schema["paths"]["/decisions"]
