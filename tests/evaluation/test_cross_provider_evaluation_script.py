from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import (
    evaluate_revenue_decline_case as evaluation_script,
)


def test_get_configured_model_name_for_gemini(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "GEMINI_MODEL",
        "test-gemini-model",
    )

    model_name = evaluation_script.get_configured_model_name(
        provider="gemini",
    )

    assert model_name == "test-gemini-model"


def test_get_configured_model_name_for_openai(
    monkeypatch,
) -> None:
    monkeypatch.setenv(
        "OPENAI_MODEL",
        "test-openai-model",
    )

    model_name = evaluation_script.get_configured_model_name(
        provider="openai",
    )

    assert model_name == "test-openai-model"


def test_get_output_path_for_gemini(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        evaluation_script,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    output_path = evaluation_script.get_output_path(
        case_id="revenue_decline_v1",
        provider="gemini",
    )

    assert output_path == (tmp_path / "gemini" / "revenue_decline_v1_eval.json")


def test_get_output_path_for_openai(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        evaluation_script,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    output_path = evaluation_script.get_output_path(
        case_id="revenue_decline_v1",
        provider="openai",
    )

    assert output_path == (tmp_path / "openai" / "revenue_decline_v1_eval.json")


def test_provider_artifact_paths_are_separate(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        evaluation_script,
        "OUTPUT_DIRECTORY",
        tmp_path,
    )

    gemini_path = evaluation_script.get_output_path(
        case_id="revenue_decline_v1",
        provider="gemini",
    )

    openai_path = evaluation_script.get_output_path(
        case_id="revenue_decline_v1",
        provider="openai",
    )

    assert gemini_path != openai_path
    assert gemini_path.parent.name == "gemini"
    assert openai_path.parent.name == "openai"


def test_evaluate_once_records_run_latency(
    monkeypatch,
) -> None:
    fake_result = SimpleNamespace(
        answer="Grounded answer.",
        grounded_claims=[],
    )

    class FakeLoop:
        def run(
            self,
            question: str,
        ):
            assert question == "Test question."

            return fake_result

    fake_loop = FakeLoop()

    monkeypatch.setattr(
        evaluation_script,
        "build_agent_loop",
        lambda **kwargs: fake_loop,
    )

    clock_values = iter(
        [
            10.0,
            10.125,
        ]
    )

    monkeypatch.setattr(
        evaluation_script,
        "perf_counter",
        lambda: next(clock_values),
    )

    run_metrics = SimpleNamespace(
        completed=True,
        status="completed",
        tool_success_rate=1.0,
        duplicate_tool_call_rate=0.0,
        model_dump=lambda mode: {
            "completed": True,
            "steps_used": 1,
            "tool_calls": 0,
            "successful_tool_calls": 0,
            "tool_failures": 0,
            "duplicate_tool_calls": 0,
        },
    )

    tool_selection = SimpleNamespace(
        used_tools=[],
        missing_required_tools=[],
        unexpected_tools=[],
        required_tool_coverage=1.0,
        passed=True,
        model_dump=lambda mode: {
            "passed": True,
        },
    )

    ground_truth = SimpleNamespace(
        results=[],
        score=1.0,
        passed=True,
        model_dump=lambda mode: {
            "passed": True,
        },
    )

    semantic_evaluation = SimpleNamespace(
        causal_overclaim=False,
        unsupported_certainty=False,
        overlap_summing_risk=False,
        recommendation_present=True,
        safety_score=1.0,
        passed=True,
        model_dump=lambda mode: {
            "passed": True,
        },
    )

    monkeypatch.setattr(
        evaluation_script,
        "evaluate_run",
        lambda result: run_metrics,
    )

    monkeypatch.setattr(
        evaluation_script,
        "evaluate_tool_selection",
        lambda case, result: tool_selection,
    )

    monkeypatch.setattr(
        evaluation_script,
        "evaluate_ground_truth",
        lambda case, result: ground_truth,
    )

    monkeypatch.setattr(
        evaluation_script,
        "evaluate_semantics",
        lambda answer, require_recommendation: semantic_evaluation,
    )

    case_config = SimpleNamespace(
        case=SimpleNamespace(
            case_id="test_case",
            question="Test question.",
        ),
        require_recommendation=True,
    )

    run = evaluation_script.evaluate_once(
        run_number=1,
        case_config=case_config,
        client=object(),
        orders=object(),
        customers=object(),
        products=object(),
        max_steps=6,
    )

    assert run["run_type"] == "quality_result"
    assert run["overall_passed"] is True

    assert run["duration_ms"] == pytest.approx(125.0)
