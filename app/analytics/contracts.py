from dataclasses import dataclass


@dataclass(frozen=True)
class RevenueComparison:
    baseline_revenue: float
    comparison_revenue: float
    absolute_change: float
    percentage_change: float


@dataclass(frozen=True)
class DriverEvidence:
    dimension: str
    value: str
    baseline_revenue: float
    comparison_revenue: float
    absolute_change: float
    percentage_change: float
    contribution_to_total_change: float


@dataclass(frozen=True)
class AnalyticsResult:
    revenue_comparison: RevenueComparison
    drivers: list[DriverEvidence]
