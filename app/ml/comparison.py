from dataclasses import dataclass

import pandas as pd

from app.ml.contracts import MLResult


@dataclass(frozen=True)
class DetectionComparison:
    total_observations: int
    baseline_anomaly_count: int
    ml_anomaly_count: int
    agreement_count: int
    disagreement_count: int
    agreement_rate: float


def compare_baseline_and_ml(
    baseline_results: pd.DataFrame,
    ml_result: MLResult,
) -> DetectionComparison:
    required_columns = {
        "date",
        "dimension",
        "value",
        "is_anomaly",
    }

    missing_columns = required_columns - set(baseline_results.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required baseline columns: {missing}")

    if baseline_results.empty:
        raise ValueError("Baseline results must not be empty.")

    if not ml_result.anomalies:
        raise ValueError("MLResult must contain anomaly observations.")

    baseline = baseline_results[
        [
            "date",
            "dimension",
            "value",
            "is_anomaly",
        ]
    ].copy()

    baseline["date"] = pd.to_datetime(baseline["date"]).dt.strftime("%Y-%m-%d")

    baseline = baseline.rename(
        columns={
            "is_anomaly": "baseline_is_anomaly",
        }
    )

    ml_dataframe = pd.DataFrame(
        [
            {
                "date": anomaly.date,
                "dimension": anomaly.dimension,
                "value": anomaly.value,
                "ml_is_anomaly": anomaly.is_anomaly,
            }
            for anomaly in ml_result.anomalies
        ]
    )

    merged = baseline.merge(
        ml_dataframe,
        on=[
            "date",
            "dimension",
            "value",
        ],
        how="inner",
        validate="one_to_one",
    )

    if merged.empty:
        raise ValueError("Baseline and ML results contain no matching observations.")

    total_observations = len(merged)

    baseline_anomaly_count = int(merged["baseline_is_anomaly"].sum())

    ml_anomaly_count = int(merged["ml_is_anomaly"].sum())

    agreement_mask = merged["baseline_is_anomaly"] == merged["ml_is_anomaly"]

    agreement_count = int(agreement_mask.sum())

    disagreement_count = total_observations - agreement_count

    agreement_rate = agreement_count / total_observations

    return DetectionComparison(
        total_observations=total_observations,
        baseline_anomaly_count=baseline_anomaly_count,
        ml_anomaly_count=ml_anomaly_count,
        agreement_count=agreement_count,
        disagreement_count=disagreement_count,
        agreement_rate=agreement_rate,
    )
