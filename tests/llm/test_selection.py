import pytest

from app.analytics.contracts import DriverEvidence
from app.llm.selection import (
    ContextBudget,
    ContextSelectionPolicy,
    SelectionMetadata,
    calculate_budget_utilization,
    calculate_omitted_count,
    calculate_retention_ratio,
    has_context_pressure,
    select_analytics_drivers,
    select_context,
    select_ml_anomalies,
    validate_context_budget,
    validate_selection_invariants,
    validate_selection_policy,
)
from app.ml.contracts import AnomalyEvidence


def build_drivers() -> list[DriverEvidence]:
    return [
        DriverEvidence(
            dimension="region",
            value="South",
            baseline_revenue=500.0,
            comparison_revenue=200.0,
            absolute_change=-300.0,
            percentage_change=-0.60,
            contribution_to_total_change=0.60,
        ),
        DriverEvidence(
            dimension="category",
            value="Computing",
            baseline_revenue=400.0,
            comparison_revenue=200.0,
            absolute_change=-200.0,
            percentage_change=-0.50,
            contribution_to_total_change=0.40,
        ),
        DriverEvidence(
            dimension="region",
            value="North",
            baseline_revenue=100.0,
            comparison_revenue=150.0,
            absolute_change=50.0,
            percentage_change=0.50,
            contribution_to_total_change=-0.10,
        ),
    ]


def build_anomalies() -> list[AnomalyEvidence]:
    return [
        AnomalyEvidence(
            date="2025-08-01",
            dimension="region",
            value="South",
            daily_revenue=50.0,
            anomaly_score=0.10,
            is_anomaly=True,
        ),
        AnomalyEvidence(
            date="2025-08-02",
            dimension="category",
            value="Computing",
            daily_revenue=40.0,
            anomaly_score=0.20,
            is_anomaly=True,
        ),
        AnomalyEvidence(
            date="2025-08-03",
            dimension="sales_channel",
            value="Partner",
            daily_revenue=60.0,
            anomaly_score=0.15,
            is_anomaly=True,
        ),
        AnomalyEvidence(
            date="2025-08-04",
            dimension="region",
            value="North",
            daily_revenue=120.0,
            anomaly_score=-0.05,
            is_anomaly=False,
        ),
    ]


def build_policy(
    analytics_driver_items: int = 5,
    ml_anomaly_items: int = 10,
) -> ContextSelectionPolicy:
    return ContextSelectionPolicy(
        budget=ContextBudget(
            analytics_driver_items=analytics_driver_items,
            ml_anomaly_items=ml_anomaly_items,
        )
    )


def build_valid_metadata() -> SelectionMetadata:
    return SelectionMetadata(
        analytics_driver_budget=5,
        analytics_drivers_available=2,
        analytics_drivers_selected=2,
        analytics_drivers_omitted=0,
        analytics_driver_retention_ratio=1.0,
        analytics_driver_budget_utilization=0.4,
        analytics_driver_context_pressure=False,
        ml_anomaly_budget=10,
        ml_anomalies_available=3,
        ml_anomalies_selected=3,
        ml_anomalies_omitted=0,
        ml_anomaly_retention_ratio=1.0,
        ml_anomaly_budget_utilization=0.3,
        ml_anomaly_context_pressure=False,
    )


def test_validate_context_budget_accepts_valid_budget() -> None:
    validate_context_budget(
        budget=ContextBudget(
            analytics_driver_items=5,
            ml_anomaly_items=10,
        )
    )


def test_validate_context_budget_rejects_negative_driver_budget() -> None:
    with pytest.raises(
        ValueError,
        match="analytics_driver_items",
    ):
        validate_context_budget(
            budget=ContextBudget(
                analytics_driver_items=-1,
                ml_anomaly_items=10,
            )
        )


def test_validate_context_budget_rejects_negative_anomaly_budget() -> None:
    with pytest.raises(
        ValueError,
        match="ml_anomaly_items",
    ):
        validate_context_budget(
            budget=ContextBudget(
                analytics_driver_items=5,
                ml_anomaly_items=-1,
            )
        )


def test_validate_selection_policy_accepts_valid_policy() -> None:
    validate_selection_policy(
        policy=build_policy(),
    )


def test_calculate_retention_ratio_returns_fraction() -> None:
    assert (
        calculate_retention_ratio(
            available=4,
            selected=2,
        )
        == 0.5
    )


def test_calculate_retention_ratio_returns_one_when_all_selected() -> None:
    assert (
        calculate_retention_ratio(
            available=3,
            selected=3,
        )
        == 1.0
    )


def test_calculate_retention_ratio_returns_one_when_nothing_available() -> None:
    assert (
        calculate_retention_ratio(
            available=0,
            selected=0,
        )
        == 1.0
    )


def test_calculate_retention_ratio_rejects_negative_available() -> None:
    with pytest.raises(
        ValueError,
        match="available",
    ):
        calculate_retention_ratio(
            available=-1,
            selected=0,
        )


def test_calculate_retention_ratio_rejects_negative_selected() -> None:
    with pytest.raises(
        ValueError,
        match="selected",
    ):
        calculate_retention_ratio(
            available=1,
            selected=-1,
        )


def test_calculate_retention_ratio_rejects_selected_above_available() -> None:
    with pytest.raises(
        ValueError,
        match="selected must not be greater",
    ):
        calculate_retention_ratio(
            available=1,
            selected=2,
        )


def test_calculate_budget_utilization_returns_fraction() -> None:
    assert (
        calculate_budget_utilization(
            budget=5,
            selected=2,
        )
        == 0.4
    )


def test_calculate_budget_utilization_returns_one_when_full() -> None:
    assert (
        calculate_budget_utilization(
            budget=3,
            selected=3,
        )
        == 1.0
    )


def test_calculate_budget_utilization_returns_one_when_budget_zero() -> None:
    assert (
        calculate_budget_utilization(
            budget=0,
            selected=0,
        )
        == 1.0
    )


def test_calculate_budget_utilization_rejects_negative_budget() -> None:
    with pytest.raises(
        ValueError,
        match="budget",
    ):
        calculate_budget_utilization(
            budget=-1,
            selected=0,
        )


def test_calculate_budget_utilization_rejects_negative_selected() -> None:
    with pytest.raises(
        ValueError,
        match="selected",
    ):
        calculate_budget_utilization(
            budget=1,
            selected=-1,
        )


def test_calculate_budget_utilization_rejects_selected_above_budget() -> None:
    with pytest.raises(
        ValueError,
        match="selected must not be greater",
    ):
        calculate_budget_utilization(
            budget=1,
            selected=2,
        )


def test_calculate_omitted_count_returns_difference() -> None:
    assert (
        calculate_omitted_count(
            available=8,
            selected=5,
        )
        == 3
    )


def test_calculate_omitted_count_returns_zero_when_all_selected() -> None:
    assert (
        calculate_omitted_count(
            available=3,
            selected=3,
        )
        == 0
    )


def test_calculate_omitted_count_handles_empty_context() -> None:
    assert (
        calculate_omitted_count(
            available=0,
            selected=0,
        )
        == 0
    )


def test_calculate_omitted_count_rejects_negative_available() -> None:
    with pytest.raises(
        ValueError,
        match="available",
    ):
        calculate_omitted_count(
            available=-1,
            selected=0,
        )


def test_calculate_omitted_count_rejects_negative_selected() -> None:
    with pytest.raises(
        ValueError,
        match="selected",
    ):
        calculate_omitted_count(
            available=1,
            selected=-1,
        )


def test_calculate_omitted_count_rejects_selected_above_available() -> None:
    with pytest.raises(
        ValueError,
        match="selected must not be greater",
    ):
        calculate_omitted_count(
            available=1,
            selected=2,
        )


def test_has_context_pressure_returns_true_when_available_exceeds_budget() -> None:
    assert has_context_pressure(
        available=8,
        budget=5,
    )


def test_has_context_pressure_returns_false_when_available_matches_budget() -> None:
    assert not has_context_pressure(
        available=5,
        budget=5,
    )


def test_has_context_pressure_returns_false_when_budget_has_capacity() -> None:
    assert not has_context_pressure(
        available=2,
        budget=5,
    )


def test_has_context_pressure_handles_zero_budget_with_available_evidence() -> None:
    assert has_context_pressure(
        available=1,
        budget=0,
    )


def test_has_context_pressure_handles_empty_zero_budget() -> None:
    assert not has_context_pressure(
        available=0,
        budget=0,
    )


def test_has_context_pressure_rejects_negative_available() -> None:
    with pytest.raises(
        ValueError,
        match="available",
    ):
        has_context_pressure(
            available=-1,
            budget=5,
        )


def test_has_context_pressure_rejects_negative_budget() -> None:
    with pytest.raises(
        ValueError,
        match="budget",
    ):
        has_context_pressure(
            available=1,
            budget=-1,
        )


def test_validate_selection_invariants_accepts_consistent_values() -> None:
    validate_selection_invariants(
        source_name="analytics_drivers",
        budget=5,
        available=8,
        selected=5,
        omitted=3,
        retention_ratio=5 / 8,
        budget_utilization=1.0,
        context_pressure=True,
    )


def test_validate_selection_invariants_rejects_selected_above_available() -> None:
    with pytest.raises(
        ValueError,
        match="selected must not be greater than available",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=5,
            available=2,
            selected=3,
            omitted=0,
            retention_ratio=1.0,
            budget_utilization=0.6,
            context_pressure=False,
        )


def test_validate_selection_invariants_rejects_selected_above_budget() -> None:
    with pytest.raises(
        ValueError,
        match="selected must not be greater than budget",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=2,
            available=5,
            selected=3,
            omitted=2,
            retention_ratio=0.6,
            budget_utilization=1.0,
            context_pressure=True,
        )


def test_validate_selection_invariants_rejects_wrong_omitted_count() -> None:
    with pytest.raises(
        ValueError,
        match="omitted must equal",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=5,
            available=8,
            selected=5,
            omitted=1,
            retention_ratio=5 / 8,
            budget_utilization=1.0,
            context_pressure=True,
        )


def test_validate_selection_invariants_rejects_wrong_retention_ratio() -> None:
    with pytest.raises(
        ValueError,
        match="retention_ratio is inconsistent",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=5,
            available=8,
            selected=5,
            omitted=3,
            retention_ratio=1.0,
            budget_utilization=1.0,
            context_pressure=True,
        )


def test_validate_selection_invariants_rejects_wrong_utilization() -> None:
    with pytest.raises(
        ValueError,
        match="budget_utilization is inconsistent",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=5,
            available=8,
            selected=5,
            omitted=3,
            retention_ratio=5 / 8,
            budget_utilization=0.5,
            context_pressure=True,
        )


def test_validate_selection_invariants_rejects_wrong_pressure() -> None:
    with pytest.raises(
        ValueError,
        match="context_pressure is inconsistent",
    ):
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=5,
            available=8,
            selected=5,
            omitted=3,
            retention_ratio=5 / 8,
            budget_utilization=1.0,
            context_pressure=False,
        )


def test_selection_metadata_validates_itself() -> None:
    result = build_valid_metadata()

    assert result.analytics_drivers_omitted == 0
    assert result.ml_anomalies_omitted == 0


def test_selection_metadata_rejects_inconsistent_analytics_metadata() -> None:
    with pytest.raises(
        ValueError,
        match="analytics_drivers: omitted must equal",
    ):
        SelectionMetadata(
            analytics_driver_budget=5,
            analytics_drivers_available=2,
            analytics_drivers_selected=2,
            analytics_drivers_omitted=1,
            analytics_driver_retention_ratio=1.0,
            analytics_driver_budget_utilization=0.4,
            analytics_driver_context_pressure=False,
            ml_anomaly_budget=10,
            ml_anomalies_available=3,
            ml_anomalies_selected=3,
            ml_anomalies_omitted=0,
            ml_anomaly_retention_ratio=1.0,
            ml_anomaly_budget_utilization=0.3,
            ml_anomaly_context_pressure=False,
        )


def test_selection_metadata_rejects_inconsistent_ml_metadata() -> None:
    with pytest.raises(
        ValueError,
        match="ml_anomalies: context_pressure is inconsistent",
    ):
        SelectionMetadata(
            analytics_driver_budget=5,
            analytics_drivers_available=2,
            analytics_drivers_selected=2,
            analytics_drivers_omitted=0,
            analytics_driver_retention_ratio=1.0,
            analytics_driver_budget_utilization=0.4,
            analytics_driver_context_pressure=False,
            ml_anomaly_budget=2,
            ml_anomalies_available=3,
            ml_anomalies_selected=2,
            ml_anomalies_omitted=1,
            ml_anomaly_retention_ratio=2 / 3,
            ml_anomaly_budget_utilization=1.0,
            ml_anomaly_context_pressure=False,
        )


def test_select_analytics_drivers_keeps_only_deterioration() -> None:
    result = select_analytics_drivers(
        drivers=build_drivers(),
        policy=build_policy(),
    )

    assert [driver.value for driver in result] == [
        "South",
        "Computing",
    ]


def test_select_analytics_drivers_preserves_existing_order() -> None:
    result = select_analytics_drivers(
        drivers=build_drivers(),
        policy=build_policy(),
    )

    assert result[0].value == "South"
    assert result[1].value == "Computing"


def test_select_analytics_drivers_applies_budget() -> None:
    result = select_analytics_drivers(
        drivers=build_drivers(),
        policy=build_policy(
            analytics_driver_items=1,
        ),
    )

    assert len(result) == 1
    assert result[0].value == "South"


def test_select_analytics_drivers_allows_zero_budget() -> None:
    result = select_analytics_drivers(
        drivers=build_drivers(),
        policy=build_policy(
            analytics_driver_items=0,
        ),
    )

    assert result == []


def test_select_ml_anomalies_keeps_only_detected_anomalies() -> None:
    result = select_ml_anomalies(
        anomalies=build_anomalies(),
        policy=build_policy(),
    )

    assert all(anomaly.is_anomaly for anomaly in result)


def test_select_ml_anomalies_orders_by_score_descending() -> None:
    result = select_ml_anomalies(
        anomalies=build_anomalies(),
        policy=build_policy(),
    )

    assert [anomaly.value for anomaly in result] == [
        "Computing",
        "Partner",
        "South",
    ]


def test_select_ml_anomalies_applies_budget() -> None:
    result = select_ml_anomalies(
        anomalies=build_anomalies(),
        policy=build_policy(
            ml_anomaly_items=2,
        ),
    )

    assert [anomaly.value for anomaly in result] == [
        "Computing",
        "Partner",
    ]


def test_select_ml_anomalies_allows_zero_budget() -> None:
    result = select_ml_anomalies(
        anomalies=build_anomalies(),
        policy=build_policy(
            ml_anomaly_items=0,
        ),
    )

    assert result == []


def test_select_context_returns_budget_metadata() -> None:
    result = select_context(
        drivers=build_drivers(),
        anomalies=build_anomalies(),
        policy=build_policy(
            analytics_driver_items=1,
            ml_anomaly_items=2,
        ),
    )

    assert result.metadata.analytics_driver_budget == 1
    assert result.metadata.analytics_drivers_available == 2
    assert result.metadata.analytics_drivers_selected == 1
    assert result.metadata.analytics_drivers_omitted == 1
    assert result.metadata.analytics_driver_retention_ratio == 0.5
    assert result.metadata.analytics_driver_budget_utilization == 1.0
    assert result.metadata.analytics_driver_context_pressure is True

    assert result.metadata.ml_anomaly_budget == 2
    assert result.metadata.ml_anomalies_available == 3
    assert result.metadata.ml_anomalies_selected == 2
    assert result.metadata.ml_anomalies_omitted == 1
    assert result.metadata.ml_anomaly_retention_ratio == pytest.approx(2 / 3)
    assert result.metadata.ml_anomaly_budget_utilization == 1.0
    assert result.metadata.ml_anomaly_context_pressure is True


def test_select_context_detects_underused_budget() -> None:
    result = select_context(
        drivers=build_drivers(),
        anomalies=build_anomalies(),
        policy=build_policy(
            analytics_driver_items=5,
            ml_anomaly_items=10,
        ),
    )

    assert result.metadata.analytics_drivers_omitted == 0

    assert result.metadata.analytics_driver_budget_utilization == 0.4

    assert result.metadata.analytics_driver_context_pressure is False

    assert result.metadata.ml_anomalies_omitted == 0

    assert result.metadata.ml_anomaly_budget_utilization == 0.3

    assert result.metadata.ml_anomaly_context_pressure is False
