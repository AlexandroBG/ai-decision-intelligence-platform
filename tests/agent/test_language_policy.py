from app.agent.language_policy import (
    OBSERVATIONAL_LANGUAGE_POLICY,
)


def test_language_policy_exists() -> None:
    assert OBSERVATIONAL_LANGUAGE_POLICY


def test_language_policy_states_observational_limit() -> None:
    assert "does not establish business causality" in OBSERVATIONAL_LANGUAGE_POLICY


def test_language_policy_contains_preferred_wording() -> None:
    expected_phrases = (
        "largest observed deterioration",
        "largest observed contribution",
        "highest-priority area to investigate",
    )

    for phrase in expected_phrases:
        assert phrase in OBSERVATIONAL_LANGUAGE_POLICY


def test_language_policy_contains_risky_wording() -> None:
    risky_phrases = (
        "root cause",
        "largest driver",
        "primary driver",
        "primary factor affecting",
    )

    for phrase in risky_phrases:
        assert phrase in OBSERVATIONAL_LANGUAGE_POLICY


def test_language_policy_warns_about_overlap() -> None:
    assert "contributions together" in OBSERVATIONAL_LANGUAGE_POLICY


def test_language_policy_frames_recommendations_as_investigation() -> None:
    assert "investigation priorities" in OBSERVATIONAL_LANGUAGE_POLICY
