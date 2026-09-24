from typing import Protocol

from app.agent.contracts import (
    AgentRunResult,
)
from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
)
from app.observability.context import (
    get_request_id,
)
from app.observability.logging import (
    get_logger,
)
from app.observability.metrics import (
    metrics,
)

logger = get_logger()


class DecisionService(Protocol):
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse: ...


class AgentRunner(Protocol):
    def run(
        self,
        question: str,
    ) -> AgentRunResult: ...


class RuntimeDecisionService:
    def __init__(
        self,
        runner: AgentRunner,
    ) -> None:
        self.runner = runner

    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        result = self.runner.run(question=request.question)

        self._log_tool_usage(result=result)

        if result.status == "completed":
            return DecisionResponse(
                status="completed",
                answer=result.answer,
                steps_used=result.steps_used,
                tool_calls=result.tool_calls,
                evidence_steps=result.evidence_steps,
            )

        return DecisionResponse(
            status="failed",
            answer=None,
            steps_used=result.steps_used,
            tool_calls=result.tool_calls,
            evidence_steps=[],
        )

    def _log_tool_usage(
        self,
        result: AgentRunResult,
    ) -> None:
        request_id = get_request_id()

        for step, observation in enumerate(
            result.history.observations,
            start=1,
        ):
            metrics.increment("tool_calls_total")

            logger.info(
                ("request_id=%s event=tool_call step=%s tool_name=%s success=%s"),
                request_id,
                step,
                observation.call.tool_name,
                str(observation.result.success).lower(),
            )


class UnavailableDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        return DecisionResponse(
            status="failed",
            answer=None,
            steps_used=0,
            tool_calls=0,
            evidence_steps=[],
        )
