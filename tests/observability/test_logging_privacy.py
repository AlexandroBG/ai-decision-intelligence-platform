import logging
from types import SimpleNamespace

from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.api.contracts import (
    DecisionRequest,
    DecisionResponse,
)
from app.api.main import (
    app,
    get_decision_service,
)
from app.api.service import (
    RuntimeDecisionService,
)
from app.llm.client import GeminiClient
from app.llm.config import LLMConfig
from app.llm.errors import (
    LLMProviderError,
)
from app.observability.context import (
    reset_request_id,
    set_request_id,
)

PRIVATE_QUESTION = "PRIVATE_QUESTION_123"
PRIVATE_ANSWER = "PRIVATE_ANSWER_456"
PRIVATE_PROVIDER_DETAIL = "PRIVATE_PROVIDER_DETAIL_789"
PRIVATE_TOOL_ARGUMENT = "PRIVATE_TOOL_ARGUMENT_321"
PRIVATE_TOOL_OUTPUT = "PRIVATE_TOOL_OUTPUT_654"
PRIVATE_LLM_PROMPT = "PRIVATE_LLM_PROMPT_987"
PRIVATE_LLM_OUTPUT = "PRIVATE_LLM_OUTPUT_741"


class CompletedDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        return DecisionResponse(
            status="completed",
            answer=PRIVATE_ANSWER,
            steps_used=1,
            tool_calls=0,
            evidence_steps=[],
        )


class ProviderFailureDecisionService:
    def decide(
        self,
        request: DecisionRequest,
    ) -> DecisionResponse:
        raise LLMProviderError(PRIVATE_PROVIDER_DETAIL)


class PrivateToolRunner:
    def run(
        self,
        question: str,
    ):
        observation = SimpleNamespace(
            call=SimpleNamespace(
                tool_name="analyze_revenue",
                arguments={
                    "private_value": (PRIVATE_TOOL_ARGUMENT),
                },
            ),
            result=SimpleNamespace(
                success=True,
                output={
                    "private_value": (PRIVATE_TOOL_OUTPUT),
                },
            ),
        )

        return SimpleNamespace(
            status="completed",
            answer=PRIVATE_ANSWER,
            steps_used=2,
            tool_calls=1,
            evidence_steps=[
                1,
            ],
            history=SimpleNamespace(
                observations=[
                    observation,
                ]
            ),
        )


class StructuredResult(BaseModel):
    value: str


def captured_messages(
    caplog,
) -> str:
    return "\n".join(
        record.getMessage() for record in caplog.records if record.name == "decisionai"
    )


def test_api_logs_do_not_include_question_or_answer(
    caplog,
) -> None:
    app.dependency_overrides[get_decision_service] = lambda: CompletedDecisionService()

    client = TestClient(app)

    try:
        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = client.post(
                "/decisions",
                json={"question": (PRIVATE_QUESTION)},
            )

        assert response.status_code == 200

        messages = captured_messages(caplog)

        assert PRIVATE_QUESTION not in messages

        assert PRIVATE_ANSWER not in messages

        assert "event=agent_completed" in messages

    finally:
        app.dependency_overrides.clear()


def test_provider_logs_do_not_include_internal_detail(
    caplog,
) -> None:
    app.dependency_overrides[get_decision_service] = lambda: (
        ProviderFailureDecisionService()
    )

    client = TestClient(app)

    try:
        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = client.post(
                "/decisions",
                json={"question": (PRIVATE_QUESTION)},
            )

        assert response.status_code == 503

        messages = captured_messages(caplog)

        assert PRIVATE_PROVIDER_DETAIL not in messages

        assert PRIVATE_QUESTION not in messages

        assert "event=provider_error" in messages

    finally:
        app.dependency_overrides.clear()


def test_tool_logs_do_not_include_arguments_or_outputs(
    caplog,
) -> None:
    token = set_request_id("privacy-test-request")

    try:
        service = RuntimeDecisionService(runner=PrivateToolRunner())

        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            response = service.decide(
                request=DecisionRequest(question=PRIVATE_QUESTION)
            )

        assert response.status == "completed"

        messages = captured_messages(caplog)

        assert PRIVATE_TOOL_ARGUMENT not in messages

        assert PRIVATE_TOOL_OUTPUT not in messages

        assert PRIVATE_QUESTION not in messages

        assert PRIVATE_ANSWER not in messages

        assert "tool_name=analyze_revenue" in messages

    finally:
        reset_request_id(token)


def test_llm_logs_do_not_include_prompt_or_response(
    monkeypatch,
    caplog,
) -> None:
    client = GeminiClient(
        config=LLMConfig(
            api_key="test-key",
            model_name=("gemini-2.5-flash"),
        )
    )

    def fake_generate_content(
        **kwargs,
    ):
        return SimpleNamespace(
            parsed={
                "value": (PRIVATE_LLM_OUTPUT),
            },
            text=None,
        )

    monkeypatch.setattr(
        client._client.models,
        "generate_content",
        fake_generate_content,
    )

    token = set_request_id("privacy-test-request")

    try:
        with caplog.at_level(
            logging.INFO,
            logger="decisionai",
        ):
            result = client.generate_structured(
                prompt=PRIVATE_LLM_PROMPT,
                response_model=(StructuredResult),
            )

        assert result.value == PRIVATE_LLM_OUTPUT

        messages = captured_messages(caplog)

        assert PRIVATE_LLM_PROMPT not in messages

        assert PRIVATE_LLM_OUTPUT not in messages

        assert "event=llm_call" in messages

        assert "model=gemini-2.5-flash" in messages

    finally:
        reset_request_id(token)
