from dataclasses import dataclass

from app.analytics.contracts import AnalyticsResult
from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
)
from app.llm.selection import (
    DEFAULT_ANALYTICS_DRIVER_BUDGET,
    DEFAULT_ML_ANOMALY_BUDGET,
    ContextBudget,
    ContextSelectionPolicy,
    SelectionMetadata,
    select_context,
)
from app.ml.contracts import MLResult


@dataclass(frozen=True)
class EvidenceBuildResult:
    evidence: EvidenceContext
    selection_metadata: SelectionMetadata


def build_evidence_context(
    question: str,
    analytics_result: AnalyticsResult,
    ml_result: MLResult,
    max_analytics_drivers: int = (DEFAULT_ANALYTICS_DRIVER_BUDGET),
    max_ml_anomalies: int = (DEFAULT_ML_ANOMALY_BUDGET),
) -> EvidenceBuildResult:
    budget = ContextBudget(
        analytics_driver_items=max_analytics_drivers,
        ml_anomaly_items=max_ml_anomalies,
    )

    policy = ContextSelectionPolicy(
        budget=budget,
    )

    selection = select_context(
        drivers=analytics_result.drivers,
        anomalies=ml_result.anomalies,
        policy=policy,
    )

    revenue = analytics_result.revenue_comparison

    revenue_evidence = EvidenceRevenue(
        evidence_id="revenue_summary_1",
        source="analytics",
        evidence_type="revenue_summary",
        baseline_revenue=revenue.baseline_revenue,
        comparison_revenue=revenue.comparison_revenue,
        absolute_change=revenue.absolute_change,
        percentage_change=revenue.percentage_change,
    )

    analytics_drivers = [
        EvidenceDriver(
            evidence_id=f"analytics_driver_{index}",
            source="analytics",
            evidence_type="driver",
            dimension=driver.dimension,
            value=driver.value,
            absolute_change=driver.absolute_change,
            percentage_change=driver.percentage_change,
            contribution_to_total_change=(driver.contribution_to_total_change),
        )
        for index, driver in enumerate(
            selection.analytics_drivers,
            start=1,
        )
    ]

    ml_anomalies = [
        EvidenceAnomaly(
            evidence_id=f"ml_anomaly_{index}",
            source="ml",
            evidence_type="anomaly",
            date=anomaly.date,
            dimension=anomaly.dimension,
            value=anomaly.value,
            daily_revenue=anomaly.daily_revenue,
            anomaly_score=anomaly.anomaly_score,
        )
        for index, anomaly in enumerate(
            selection.ml_anomalies,
            start=1,
        )
    ]

    evidence = EvidenceContext(
        question=question,
        revenue=revenue_evidence,
        analytics_drivers=analytics_drivers,
        ml_anomalies=ml_anomalies,
    )

    return EvidenceBuildResult(
        evidence=evidence,
        selection_metadata=selection.metadata,
    )
