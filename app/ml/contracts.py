from dataclasses import dataclass


@dataclass(frozen=True)
class AnomalyEvidence:
    date: str
    dimension: str
    value: str
    daily_revenue: float
    anomaly_score: float
    is_anomaly: bool


@dataclass(frozen=True)
class MLResult:
    anomalies: list[AnomalyEvidence]
