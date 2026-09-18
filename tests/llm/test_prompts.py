from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
)
from app.llm.prompts import (
    SYSTEM_PROMPT,
    build_evidence_prompt,
)


def build_evidence_context() -> EvidenceContext:
    return EvidenceContext(
        question="Why did revenue decline?",
        revenue=EvidenceRevenue(
            evidence_id="revenue_summary_1",
            source="analytics",
            evidence_type="revenue_summary",
            baseline_revenue=1000.0,
            comparison_revenue=700.0,
            absolute_change=-300.0,
            percentage_change=-0.30,
        ),
        analytics_drivers=[
            EvidenceDriver(
                evidence_id="analytics_driver_1",
                source="analytics",
                evidence_type="driver",
                dimension="region",
                value="South",
                absolute_change=-250.0,
                percentage_change=-0.50,
                contribution_to_total_change=0.83,
            )
        ],
        ml_anomalies=[
            EvidenceAnomaly(
                evidence_id="ml_anomaly_1",
                source="ml",
                evidence_type="anomaly",
                date="2025-08-10",
                dimension="region",
                value="South",
                daily_revenue=50.0,
                anomaly_score=0.12,
            )
        ],
    )


def test_system_prompt_contains_grounding_rules() -> None:
    assert "Use only the evidence provided" in SYSTEM_PROMPT

    assert "Do not invent facts" in SYSTEM_PROMPT


def test_system_prompt_requires_fact_grounding() -> None:
    assert 'claim_type="fact"' in SYSTEM_PROMPT

    assert (
        "Every factual claim must reference "
        "at least one valid evidence_id." in SYSTEM_PROMPT
    )


def test_system_prompt_requires_inference_grounding() -> None:
    assert 'claim_type="inference"' in SYSTEM_PROMPT

    assert (
        "Every inference must reference "
        "at least one valid evidence_id." in SYSTEM_PROMPT
    )


def test_system_prompt_allows_unknown_without_evidence() -> None:
    assert 'claim_type="unknown"' in SYSTEM_PROMPT

    assert "Unknown claims may use an empty evidence_ids list." in SYSTEM_PROMPT


def test_system_prompt_defines_grounded_claims_as_canonical() -> None:
    assert "grounded_claims are the canonical source of truth." in SYSTEM_PROMPT

    assert (
        "Do not create separate duplicate fact, inference, "
        "or unknown lists." in SYSTEM_PROMPT
    )


def test_system_prompt_prohibits_invented_evidence_ids() -> None:
    assert "Only reference evidence IDs that appear" in SYSTEM_PROMPT

    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert "Do not invent evidence IDs." in prompt


def test_system_prompt_prohibits_cross_dimension_contribution_summing() -> None:
    assert (
        "Do not add contribution values across different dimensions." in SYSTEM_PROMPT
    )

    assert "Do not sum contribution_to_total_change values" in SYSTEM_PROMPT

    assert "region, category, and sales channel" in SYSTEM_PROMPT


def test_system_prompt_says_contribution_is_not_causal() -> None:
    assert "It is not a causal attribution." in SYSTEM_PROMPT


def test_system_prompt_defines_anomaly_boundary() -> None:
    assert "An anomaly does not establish a root cause." in SYSTEM_PROMPT


def test_system_prompt_prohibits_causal_overclaiming() -> None:
    assert "establish causality" in SYSTEM_PROMPT

    assert "Never claim that a driver or anomaly caused" in SYSTEM_PROMPT


def test_build_evidence_prompt_includes_question() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert "Why did revenue decline?" in prompt


def test_build_evidence_prompt_includes_structured_evidence() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert "revenue_summary_1" in prompt
    assert "analytics_driver_1" in prompt
    assert "ml_anomaly_1" in prompt
    assert "South" in prompt


def test_build_evidence_prompt_requires_grounded_claims() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert "Use grounded_claims as the only canonical list" in prompt


def test_build_evidence_prompt_restricts_evidence_ids() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert (
        "Every fact and inference must cite one or more valid evidence IDs." in prompt
    )

    assert "Do not invent evidence IDs." in prompt


def test_build_evidence_prompt_contains_contribution_boundary() -> None:
    prompt = build_evidence_prompt(
        evidence=build_evidence_context(),
    )

    assert "Do not add contribution values across different dimensions." in prompt

    assert "Do not sum contribution_to_total_change values" in prompt
