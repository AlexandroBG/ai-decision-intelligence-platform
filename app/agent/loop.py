import json
from collections.abc import Callable

from app.agent.contracts import (
    AgentDecision,
    AgentFinalAction,
    AgentHistory,
    AgentObservation,
    AgentRunResult,
    AgentToolAction,
)
from app.agent.grounding import (
    AgentGroundingError,
    evidence_steps_to_ids,
    validate_agent_grounded_claims,
)
from app.tools.contracts import ToolCall
from app.tools.executor import ToolExecutor

DecisionFunction = Callable[
    [str, AgentHistory],
    AgentDecision,
]


class AgentLoop:
    def __init__(
        self,
        executor: ToolExecutor,
        decide: DecisionFunction,
        max_steps: int = 5,
        max_tool_failures: int = 2,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero.")

        if max_tool_failures < 0:
            raise ValueError("max_tool_failures must not be negative.")

        self._executor = executor
        self._decide = decide
        self._max_steps = max_steps
        self._max_tool_failures = max_tool_failures

    def run(
        self,
        question: str,
    ) -> AgentRunResult:
        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("Agent question must not be empty.")

        history = AgentHistory()
        executed_calls: set[str] = set()
        tool_failure_count = 0

        for step_index in range(
            1,
            self._max_steps + 1,
        ):
            decision = self._decide(
                normalized_question,
                history,
            )

            action = decision.action

            if isinstance(
                action,
                AgentFinalAction,
            ):
                evidence_error = self._validate_final_evidence(
                    action=action,
                    history=history,
                )

                if evidence_error is not None:
                    return self._build_terminated_result(
                        status="invalid_final_evidence",
                        reason=evidence_error,
                        step_index=step_index,
                        history=history,
                        tool_failure_count=(tool_failure_count),
                    )

                grounding_error = self._validate_final_grounding(
                    action=action,
                    history=history,
                )

                if grounding_error is not None:
                    return self._build_terminated_result(
                        status="invalid_final_grounding",
                        reason=grounding_error,
                        step_index=step_index,
                        history=history,
                        tool_failure_count=(tool_failure_count),
                    )

                return AgentRunResult(
                    answer=action.answer,
                    evidence_steps=(action.evidence_steps),
                    grounded_claims=(action.grounded_claims),
                    status="completed",
                    termination_reason=None,
                    steps_used=step_index,
                    tool_calls=len(history.observations),
                    tool_failures=tool_failure_count,
                    history=history,
                )

            if isinstance(
                action,
                AgentToolAction,
            ):
                if tool_failure_count >= self._max_tool_failures:
                    return self._build_terminated_result(
                        status=("tool_failure_limit_reached"),
                        reason=(
                            "Agent exceeded the allowed number of failed tool calls."
                        ),
                        step_index=step_index,
                        history=history,
                        tool_failure_count=(tool_failure_count),
                    )

                call_signature = self._build_call_signature(call=action.call)

                if call_signature in executed_calls:
                    return self._build_terminated_result(
                        status="duplicate_tool_call",
                        reason=("Agent attempted to repeat an identical tool call."),
                        step_index=step_index,
                        history=history,
                        tool_failure_count=(tool_failure_count),
                    )

                executed_calls.add(call_signature)

                result = self._executor.execute(call=action.call)

                observation = AgentObservation(
                    call=action.call,
                    result=result,
                )

                history.observations.append(observation)

                if not result.success:
                    tool_failure_count += 1

                continue

            raise RuntimeError("Unsupported agent action.")

        return self._build_terminated_result(
            status="max_steps_reached",
            reason=(
                "Agent reached the maximum number of steps without a final answer."
            ),
            step_index=self._max_steps,
            history=history,
            tool_failure_count=tool_failure_count,
        )

    @staticmethod
    def _validate_final_evidence(
        action: AgentFinalAction,
        history: AgentHistory,
    ) -> str | None:
        observation_count = len(history.observations)

        if observation_count == 0 and action.evidence_steps:
            return (
                "Final answer referenced tool evidence when no tool observations exist."
            )

        if observation_count == 0 and action.grounded_claims:
            return (
                "Final answer included grounded claims when no tool observations exist."
            )

        if observation_count > 0 and not action.evidence_steps:
            return "Final answer must reference at least one tool observation."

        if any(step > observation_count for step in action.evidence_steps):
            return "Final answer referenced an unknown tool observation step."

        return None

    @staticmethod
    def _validate_final_grounding(
        action: AgentFinalAction,
        history: AgentHistory,
    ) -> str | None:
        observation_count = len(history.observations)

        if observation_count == 0:
            return None

        if not action.grounded_claims:
            return "Final answer must include grounded claims after using tools."

        try:
            validate_agent_grounded_claims(
                claims=action.grounded_claims,
                history=history,
            )
        except AgentGroundingError as exc:
            return str(exc)

        declared_evidence_ids = set(
            evidence_steps_to_ids(evidence_steps=(action.evidence_steps))
        )

        claimed_evidence_ids = {
            evidence_id
            for claim in action.grounded_claims
            for evidence_id in claim.evidence_ids
        }

        if claimed_evidence_ids != declared_evidence_ids:
            return (
                "Final evidence steps must match the evidence used by grounded claims."
            )

        return None

    @staticmethod
    def _build_terminated_result(
        status: str,
        reason: str,
        step_index: int,
        history: AgentHistory,
        tool_failure_count: int,
    ) -> AgentRunResult:
        return AgentRunResult(
            answer=None,
            evidence_steps=[],
            grounded_claims=[],
            status=status,
            termination_reason=reason,
            steps_used=step_index,
            tool_calls=len(history.observations),
            tool_failures=tool_failure_count,
            history=history,
        )

    @staticmethod
    def _build_call_signature(
        call: ToolCall,
    ) -> str:
        serialized_arguments = json.dumps(
            call.arguments,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )

        return f"{call.tool_name}:{serialized_arguments}"
