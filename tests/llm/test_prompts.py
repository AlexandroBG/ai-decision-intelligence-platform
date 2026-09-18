from app.llm.contracts import (
    EvidenceContext,
    EvidenceRevenue,
)
from app.llm.prompts import (
    DECISION_INTELLIGENCE_SYSTEM_PROMPT,
    build_evidence_prompt,
)


def build_evidence() -> EvidenceContext:
    return EvidenceContext(
        question="Why did revenue decline?",
        revenue=EvidenceRevenue(
            baseline_revenue=1000.0,
            comparison_revenue=700.0,
            absolute_change=-300.0,
            percentage_change=-0.30,
        ),
    )


def test_system_prompt_contains_grounding_rules() -> None:
    prompt = DECISION_INTELLIGENCE_SYSTEM_PROMPT

    assert "Do not invent" in prompt
    assert "Do not claim causality" in prompt
    assert "source of truth" in prompt


def test_system_prompt_contains_certainty_levels() -> None:
    prompt = DECISION_INTELLIGENCE_SYSTEM_PROMPT

    assert "FACT" in prompt
    assert "INFERENCE" in prompt
    assert "UNKNOWN" in prompt


def test_system_prompt_prohibits_cross_dimension_contribution_summing() -> None:
    prompt = DECISION_INTELLIGENCE_SYSTEM_PROMPT

    assert (
        "Contribution values from different dimensions "
        "MUST NOT be summed together" in prompt
    )


def test_system_prompt_says_contribution_is_not_causal() -> None:
    prompt = DECISION_INTELLIGENCE_SYSTEM_PROMPT

    assert "does NOT establish causal attribution" in prompt


def test_system_prompt_defines_anomaly_boundary() -> None:
    prompt = DECISION_INTELLIGENCE_SYSTEM_PROMPT

    assert "An anomaly does NOT prove" in prompt
    assert "anomaly_score" in prompt


def test_build_evidence_prompt_includes_question() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence(),
    )

    assert "Why did revenue decline?" in prompt


def test_build_evidence_prompt_includes_structured_evidence() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence(),
    )

    assert '"absolute_change": -300.0' in prompt
    assert '"percentage_change": -0.3' in prompt


def test_build_evidence_prompt_repeats_contribution_boundary() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence(),
    )

    assert "Do not add contribution values across different dimensions." in prompt
