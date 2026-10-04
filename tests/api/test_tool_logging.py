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

PRIVATE_ARGUMENT = "PRIVATE_ARGUMENT_123"
PRIVATE_OUTPUT = "PRIVATE_OUTPUT_456"
PRIVATE_ERROR = "PRIVATE_ERROR_789"


class FakeRunner:
    def run(
        self,
        question: str,
    ):
        first_observation = SimpleNamespace(
            call=SimpleNamespace(
                tool_name="analyze_revenue",
                arguments={
                    "private_value": PRIVATE_ARGUMENT,
                },
            ),
            result=SimpleNamespace(
                success=True,
                output={
                    "private_value": PRIVATE_OUTPUT,
                },
                error=None,
            ),
        )

        second_observation = SimpleNamespace(
            call=SimpleNamespace(
                tool_name=("analyze_revenue_drivers"),
                arguments={
                    "private_value": PRIVATE_ARGUMENT,
                },
            ),
            result=SimpleNamespace(
                success=False,
                output=None,
                error=PRIVATE_ERROR,
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

        summary_records = [
            record
            for record in caplog.records
            if (
                record.name == "decisionai"
                and "successful_tool_calls=" in record.getMessage()
            )
        ]

        assert len(summary_records) == 1
        summary_message = summary_records[0].getMessage()
        assert summary_message == (
            f"request_id={request_id} tool_calls=2 "
            "successful_tool_calls=1 failed_tool_calls=1"
        )

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

        combined_messages = f"{first_message}\n{second_message}\n{summary_message}"

        assert PRIVATE_ARGUMENT not in combined_messages

        assert PRIVATE_OUTPUT not in combined_messages

        assert PRIVATE_ERROR not in combined_messages

    finally:
        reset_request_id(token)


def test_runtime_service_logs_separate_summaries_per_request_id(
    caplog,
) -> None:
    service = RuntimeDecisionService(runner=FakeRunner())

    with caplog.at_level(
        logging.INFO,
        logger="decisionai",
    ):
        for request_id in ("first-request", "second-request"):
            token = set_request_id(request_id)

            try:
                service.decide(
                    request=DecisionRequest(question="What happened?")
                )
            finally:
                reset_request_id(token)

    summary_messages = [
        record.getMessage()
        for record in caplog.records
        if (
            record.name == "decisionai"
            and "successful_tool_calls=" in record.getMessage()
        )
    ]

    assert summary_messages == [
        "request_id=first-request tool_calls=2 successful_tool_calls=1 failed_tool_calls=1",
        "request_id=second-request tool_calls=2 successful_tool_calls=1 failed_tool_calls=1",
    ]
