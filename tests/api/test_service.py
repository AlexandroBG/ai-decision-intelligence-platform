from app.agent.contracts import (
    AgentHistory,
    AgentRunResult,
)
from app.api.contracts import (
    DecisionRequest,
)
from app.api.service import (
    RuntimeDecisionService,
)


class FakeAgentRunner:
    def __init__(
        self,
        result: AgentRunResult,
    ) -> None:
        self.result = result
        self.questions: list[str] = []

    def run(
        self,
        question: str,
    ) -> AgentRunResult:
        self.questions.append(question)

        return self.result


def build_completed_result() -> AgentRunResult:
    return AgentRunResult(
        answer=("Revenue decreased by 28.06%."),
        evidence_steps=[],
        grounded_claims=[],
        status="completed",
        termination_reason=None,
        steps_used=1,
        tool_calls=0,
        tool_failures=0,
        history=AgentHistory(),
    )


def build_failed_result() -> AgentRunResult:
    return AgentRunResult(
        answer=None,
        evidence_steps=[],
        grounded_claims=[],
        status="max_steps_reached",
        termination_reason=("Maximum agent steps reached."),
        steps_used=5,
        tool_calls=0,
        tool_failures=0,
        history=AgentHistory(),
    )


def test_runtime_service_passes_question_to_runner() -> None:
    runner = FakeAgentRunner(result=build_completed_result())

    service = RuntimeDecisionService(runner=runner)

    service.decide(request=DecisionRequest(question=("What happened to revenue?")))

    assert runner.questions == ["What happened to revenue?"]


def test_runtime_service_maps_completed_run() -> None:
    runner = FakeAgentRunner(result=build_completed_result())

    service = RuntimeDecisionService(runner=runner)

    response = service.decide(request=DecisionRequest(question="What happened?"))

    assert response.status == "completed"

    assert response.answer == "Revenue decreased by 28.06%."

    assert response.steps_used == 1

    assert response.tool_calls == 0

    assert response.evidence_steps == []


def test_runtime_service_maps_guardrail_termination_to_failed() -> None:
    runner = FakeAgentRunner(result=build_failed_result())

    service = RuntimeDecisionService(runner=runner)

    response = service.decide(request=DecisionRequest(question="What happened?"))

    assert response.status == "failed"

    assert response.answer is None

    assert response.steps_used == 5

    assert response.tool_calls == 0

    assert response.evidence_steps == []


def test_runtime_service_does_not_expose_termination_reason() -> None:
    runner = FakeAgentRunner(result=build_failed_result())

    service = RuntimeDecisionService(runner=runner)

    response = service.decide(request=DecisionRequest(question="What happened?"))

    dumped = response.model_dump()

    assert "termination_reason" not in dumped
