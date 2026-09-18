from dataclasses import dataclass
from math import isclose

from app.analytics.contracts import DriverEvidence
from app.ml.contracts import AnomalyEvidence

DEFAULT_ANALYTICS_DRIVER_BUDGET = 5
DEFAULT_ML_ANOMALY_BUDGET = 10


def calculate_retention_ratio(
    available: int,
    selected: int,
) -> float:
    if available < 0:
        raise ValueError("available must be greater than or equal to 0.")

    if selected < 0:
        raise ValueError("selected must be greater than or equal to 0.")

    if selected > available:
        raise ValueError("selected must not be greater than available.")

    if available == 0:
        return 1.0

    return selected / available


def calculate_budget_utilization(
    budget: int,
    selected: int,
) -> float:
    if budget < 0:
        raise ValueError("budget must be greater than or equal to 0.")

    if selected < 0:
        raise ValueError("selected must be greater than or equal to 0.")

    if selected > budget:
        raise ValueError("selected must not be greater than budget.")

    if budget == 0:
        return 1.0

    return selected / budget


def calculate_omitted_count(
    available: int,
    selected: int,
) -> int:
    if available < 0:
        raise ValueError("available must be greater than or equal to 0.")

    if selected < 0:
        raise ValueError("selected must be greater than or equal to 0.")

    if selected > available:
        raise ValueError("selected must not be greater than available.")

    return available - selected


def has_context_pressure(
    available: int,
    budget: int,
) -> bool:
    if available < 0:
        raise ValueError("available must be greater than or equal to 0.")

    if budget < 0:
        raise ValueError("budget must be greater than or equal to 0.")

    return available > budget


def validate_selection_invariants(
    *,
    source_name: str,
    budget: int,
    available: int,
    selected: int,
    omitted: int,
    retention_ratio: float,
    budget_utilization: float,
    context_pressure: bool,
) -> None:
    if budget < 0:
        raise ValueError(f"{source_name}: budget must be greater than or equal to 0.")

    if available < 0:
        raise ValueError(
            f"{source_name}: available must be greater than or equal to 0."
        )

    if selected < 0:
        raise ValueError(f"{source_name}: selected must be greater than or equal to 0.")

    if omitted < 0:
        raise ValueError(f"{source_name}: omitted must be greater than or equal to 0.")

    if selected > available:
        raise ValueError(f"{source_name}: selected must not be greater than available.")

    if selected > budget:
        raise ValueError(f"{source_name}: selected must not be greater than budget.")

    expected_omitted = calculate_omitted_count(
        available=available,
        selected=selected,
    )

    if omitted != expected_omitted:
        raise ValueError(f"{source_name}: omitted must equal available minus selected.")

    expected_retention = calculate_retention_ratio(
        available=available,
        selected=selected,
    )

    if not isclose(
        retention_ratio,
        expected_retention,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ):
        raise ValueError(
            f"{source_name}: retention_ratio is inconsistent "
            "with available and selected."
        )

    expected_utilization = calculate_budget_utilization(
        budget=budget,
        selected=selected,
    )

    if not isclose(
        budget_utilization,
        expected_utilization,
        rel_tol=1e-9,
        abs_tol=1e-12,
    ):
        raise ValueError(
            f"{source_name}: budget_utilization is inconsistent "
            "with budget and selected."
        )

    expected_pressure = has_context_pressure(
        available=available,
        budget=budget,
    )

    if context_pressure is not expected_pressure:
        raise ValueError(
            f"{source_name}: context_pressure is inconsistent "
            "with available and budget."
        )


@dataclass(frozen=True)
class ContextBudget:
    analytics_driver_items: int = DEFAULT_ANALYTICS_DRIVER_BUDGET
    ml_anomaly_items: int = DEFAULT_ML_ANOMALY_BUDGET


@dataclass(frozen=True)
class ContextSelectionPolicy:
    budget: ContextBudget


@dataclass(frozen=True)
class SelectionMetadata:
    analytics_driver_budget: int
    analytics_drivers_available: int
    analytics_drivers_selected: int
    analytics_drivers_omitted: int
    analytics_driver_retention_ratio: float
    analytics_driver_budget_utilization: float
    analytics_driver_context_pressure: bool

    ml_anomaly_budget: int
    ml_anomalies_available: int
    ml_anomalies_selected: int
    ml_anomalies_omitted: int
    ml_anomaly_retention_ratio: float
    ml_anomaly_budget_utilization: float
    ml_anomaly_context_pressure: bool

    def __post_init__(self) -> None:
        validate_selection_invariants(
            source_name="analytics_drivers",
            budget=self.analytics_driver_budget,
            available=self.analytics_drivers_available,
            selected=self.analytics_drivers_selected,
            omitted=self.analytics_drivers_omitted,
            retention_ratio=(self.analytics_driver_retention_ratio),
            budget_utilization=(self.analytics_driver_budget_utilization),
            context_pressure=(self.analytics_driver_context_pressure),
        )

        validate_selection_invariants(
            source_name="ml_anomalies",
            budget=self.ml_anomaly_budget,
            available=self.ml_anomalies_available,
            selected=self.ml_anomalies_selected,
            omitted=self.ml_anomalies_omitted,
            retention_ratio=(self.ml_anomaly_retention_ratio),
            budget_utilization=(self.ml_anomaly_budget_utilization),
            context_pressure=(self.ml_anomaly_context_pressure),
        )


@dataclass(frozen=True)
class ContextSelectionResult:
    analytics_drivers: list[DriverEvidence]
    ml_anomalies: list[AnomalyEvidence]
    metadata: SelectionMetadata


def validate_context_budget(
    budget: ContextBudget,
) -> None:
    if budget.analytics_driver_items < 0:
        raise ValueError("analytics_driver_items must be greater than or equal to 0.")

    if budget.ml_anomaly_items < 0:
        raise ValueError("ml_anomaly_items must be greater than or equal to 0.")


def validate_selection_policy(
    policy: ContextSelectionPolicy,
) -> None:
    validate_context_budget(
        budget=policy.budget,
    )


def select_analytics_drivers(
    drivers: list[DriverEvidence],
    policy: ContextSelectionPolicy,
) -> list[DriverEvidence]:
    validate_selection_policy(
        policy=policy,
    )

    deteriorating_drivers = [driver for driver in drivers if driver.absolute_change < 0]

    return deteriorating_drivers[: policy.budget.analytics_driver_items]


def select_ml_anomalies(
    anomalies: list[AnomalyEvidence],
    policy: ContextSelectionPolicy,
) -> list[AnomalyEvidence]:
    validate_selection_policy(
        policy=policy,
    )

    detected_anomalies = [anomaly for anomaly in anomalies if anomaly.is_anomaly]

    ranked_anomalies = sorted(
        detected_anomalies,
        key=lambda anomaly: anomaly.anomaly_score,
        reverse=True,
    )

    return ranked_anomalies[: policy.budget.ml_anomaly_items]


def select_context(
    drivers: list[DriverEvidence],
    anomalies: list[AnomalyEvidence],
    policy: ContextSelectionPolicy,
) -> ContextSelectionResult:
    validate_selection_policy(
        policy=policy,
    )

    eligible_drivers = [driver for driver in drivers if driver.absolute_change < 0]

    eligible_anomalies = [anomaly for anomaly in anomalies if anomaly.is_anomaly]

    selected_drivers = select_analytics_drivers(
        drivers=drivers,
        policy=policy,
    )

    selected_anomalies = select_ml_anomalies(
        anomalies=anomalies,
        policy=policy,
    )

    driver_available = len(eligible_drivers)

    driver_selected = len(selected_drivers)

    driver_budget = policy.budget.analytics_driver_items

    anomaly_available = len(eligible_anomalies)

    anomaly_selected = len(selected_anomalies)

    anomaly_budget = policy.budget.ml_anomaly_items

    metadata = SelectionMetadata(
        analytics_driver_budget=driver_budget,
        analytics_drivers_available=driver_available,
        analytics_drivers_selected=driver_selected,
        analytics_drivers_omitted=(
            calculate_omitted_count(
                available=driver_available,
                selected=driver_selected,
            )
        ),
        analytics_driver_retention_ratio=(
            calculate_retention_ratio(
                available=driver_available,
                selected=driver_selected,
            )
        ),
        analytics_driver_budget_utilization=(
            calculate_budget_utilization(
                budget=driver_budget,
                selected=driver_selected,
            )
        ),
        analytics_driver_context_pressure=(
            has_context_pressure(
                available=driver_available,
                budget=driver_budget,
            )
        ),
        ml_anomaly_budget=anomaly_budget,
        ml_anomalies_available=anomaly_available,
        ml_anomalies_selected=anomaly_selected,
        ml_anomalies_omitted=(
            calculate_omitted_count(
                available=anomaly_available,
                selected=anomaly_selected,
            )
        ),
        ml_anomaly_retention_ratio=(
            calculate_retention_ratio(
                available=anomaly_available,
                selected=anomaly_selected,
            )
        ),
        ml_anomaly_budget_utilization=(
            calculate_budget_utilization(
                budget=anomaly_budget,
                selected=anomaly_selected,
            )
        ),
        ml_anomaly_context_pressure=(
            has_context_pressure(
                available=anomaly_available,
                budget=anomaly_budget,
            )
        ),
    )

    return ContextSelectionResult(
        analytics_drivers=selected_drivers,
        ml_anomalies=selected_anomalies,
        metadata=metadata,
    )
