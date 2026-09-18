from app.analytics.contracts import AnalyticsResult
from app.llm.contracts import (
    EvidenceAnomaly,
    EvidenceContext,
    EvidenceDriver,
    EvidenceRevenue,
)
from app.ml.contracts import MLResult

DEFAULT_MAX_ANALYTICS_DRIVERS = 5
DEFAULT_MAX_ML_ANOMALIES = 10


def build_evidence_context(
    question: str,
    analytics_result: AnalyticsResult,
    ml_result: MLResult,
    max_analytics_drivers: int = DEFAULT_MAX_ANALYTICS_DRIVERS,
    max_ml_anomalies: int = DEFAULT_MAX_ML_ANOMALIES,
) -> EvidenceContext:
    if max_analytics_drivers < 0:
        raise ValueError("max_analytics_drivers must be greater than or equal to 0.")

    if max_ml_anomalies < 0:
        raise ValueError("max_ml_anomalies must be greater than or equal to 0.")

    revenue = analytics_result.revenue_comparison

    revenue_evidence = EvidenceRevenue(
        baseline_revenue=revenue.baseline_revenue,
        comparison_revenue=revenue.comparison_revenue,
        absolute_change=revenue.absolute_change,
        percentage_change=revenue.percentage_change,
    )

    selected_drivers = analytics_result.drivers[:max_analytics_drivers]

    analytics_drivers = [
        EvidenceDriver(
            dimension=driver.dimension,
            value=driver.value,
            absolute_change=driver.absolute_change,
            percentage_change=driver.percentage_change,
            contribution_to_total_change=(driver.contribution_to_total_change),
        )
        for driver in selected_drivers
    ]

    detected_anomalies = [
        anomaly for anomaly in ml_result.anomalies if anomaly.is_anomaly
    ]

    ranked_anomalies = sorted(
        detected_anomalies,
        key=lambda anomaly: anomaly.anomaly_score,
        reverse=True,
    )

    selected_anomalies = ranked_anomalies[:max_ml_anomalies]

    ml_anomalies = [
        EvidenceAnomaly(
            date=anomaly.date,
            dimension=anomaly.dimension,
            value=anomaly.value,
            daily_revenue=anomaly.daily_revenue,
            anomaly_score=anomaly.anomaly_score,
        )
        for anomaly in selected_anomalies
    ]

    return EvidenceContext(
        question=question,
        revenue=revenue_evidence,
        analytics_drivers=analytics_drivers,
        ml_anomalies=ml_anomalies,
    )
