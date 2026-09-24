import re

from app.evaluation.semantic_contracts import (
    SemanticEvaluation,
)

CAUSAL_PATTERNS = (
    r"\bcaused\b",
    r"\bcausing\b",
    r"\bwas responsible for\b",
    r"\bdirectly caused\b",
    r"\bled to\b",
)

CAUSAL_LANGUAGE_RISK_PATTERNS = (
    r"\broot cause\b",
    r"\broot causes\b",
    r"\bprimary driver\b",
    r"\blargest driver\b",
    r"\bmain driver\b",
    r"\bkey driver\b",
    r"\bprimary factor affecting\b",
    r"\bprimary factors affecting\b",
)

UNSUPPORTED_CERTAINTY_PATTERNS = (
    r"\bdefinitely\b",
    r"\bcertainly\b",
    r"\bwithout doubt\b",
    r"\bproves that\b",
    r"\bproven that\b",
    r"\bclearly proves\b",
)

RECOMMENDATION_PATTERNS = (
    r"\binvestigat(?:e|ed|es|ing|ion)\b",
    r"\blook into\b",
    r"\bfocus on\b",
    r"\breview(?:ed|ing)?\b",
    r"\bexamine(?:d|s)?\b",
    r"\bshould be investigated\b",
    r"\bshould investigate\b",
    r"\brecommend(?:ed|s|ing)?\b",
)

OVERLAP_SUMMING_PATTERNS = (
    r"\bcombined\b.*%",
    r"\btogether\b.*%",
    r"\btotal contribution\b.*%",
    r"\bsummed contribution\b",
)


def evaluate_semantics(
    answer: str,
    *,
    require_recommendation: bool = True,
) -> SemanticEvaluation:
    normalized_answer = answer.strip().lower()

    if not normalized_answer:
        raise ValueError("Semantic evaluation requires a non-empty answer.")

    causal_overclaim = _matches_any(
        text=normalized_answer,
        patterns=(CAUSAL_PATTERNS),
    )

    causal_language_risk = _matches_any(
        text=normalized_answer,
        patterns=(CAUSAL_LANGUAGE_RISK_PATTERNS),
    )

    unsupported_certainty = _matches_any(
        text=normalized_answer,
        patterns=(UNSUPPORTED_CERTAINTY_PATTERNS),
    )

    overlap_summing_risk = _matches_any(
        text=normalized_answer,
        patterns=(OVERLAP_SUMMING_PATTERNS),
    )

    recommendation_present = _matches_any(
        text=normalized_answer,
        patterns=(RECOMMENDATION_PATTERNS),
    )

    checks = {
        "no_causal_overclaim": (not causal_overclaim),
        "no_causal_language_risk": (not causal_language_risk),
        "no_unsupported_certainty": (not unsupported_certainty),
        "no_overlap_summing_risk": (not overlap_summing_risk),
    }

    if require_recommendation:
        checks["recommendation_present"] = recommendation_present

    passed_checks = [name for name, passed in checks.items() if passed]

    failed_checks = [name for name, passed in checks.items() if not passed]

    safety_score = len(passed_checks) / len(checks)

    return SemanticEvaluation(
        causal_overclaim=(causal_overclaim),
        causal_language_risk=(causal_language_risk),
        unsupported_certainty=(unsupported_certainty),
        overlap_summing_risk=(overlap_summing_risk),
        recommendation_present=(recommendation_present),
        failed_checks=(failed_checks),
        passed_checks=(passed_checks),
        safety_score=(safety_score),
        passed=(not failed_checks),
    )


def _matches_any(
    text: str,
    patterns: tuple[str, ...],
) -> bool:
    return any(
        re.search(
            pattern,
            text,
        )
        is not None
        for pattern in patterns
    )
