import logging
from types import SimpleNamespace

from app.api.contracts import (
    DecisionRequest,
)
from app.api.service import (
    RuntimeDecisionService,
)
from app.observability.context import (
    reset_request_id,
    set_request_id,
)


class FakeRunner:
    def run(
        self,
        question: str,
    ):
        first_observation = SimpleNamespace(
            call=SimpleNamespace(
                tool_name="analyze_revenue",
            ),
            result=SimpleNamespace(
                success=True,
            ),
        )

        second_observation = SimpleNamespace(
            call=SimpleNamespace(
                tool_name="analyze_revenue_drivers",
            ),
            result=SimpleNamespace(
                success=False,
            ),
        )

        return SimpleNamespace(
            status="completed",
            answer="Result.",
            steps_used=3,
            tool_calls=2,
            evidence_steps=[
                1,
                2,
            ],
            history=SimpleNamespace(
                observations=[
                    first_observation,
                    second_observation,
                ]
            ),
        )


def test_runtime_service_logs_tool_usage(
    caplog,
) -> None:
    request_id = "test-request-id"

    token = set_request_id(request_id)

    try:
        service = RuntimeDecisionService(runner=FakeRunner())

        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = service.decide(
                request=DecisionRequest(question="What happened?")
            )

        assert response.status == "completed"

        tool_records = [
            record
            for record in caplog.records
            if (
                record.name == "decisionai" and "event=tool_call" in record.getMessage()
            )
        ]

        assert len(tool_records) == 2

        first_message = tool_records[0].getMessage()

        second_message = tool_records[1].getMessage()

        assert f"request_id={request_id}" in first_message

        assert "step=1" in first_message

        assert "tool_name=analyze_revenue" in first_message

        assert "success=true" in first_message

        assert f"request_id={request_id}" in second_message

        assert "step=2" in second_message

        assert "tool_name=analyze_revenue_drivers" in second_message

        assert "success=false" in second_message

    finally:
        reset_request_id(token)
