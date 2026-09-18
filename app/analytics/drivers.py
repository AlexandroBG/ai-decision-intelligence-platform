import pandas as pd

from app.analytics.contracts import DriverEvidence


def build_driver_candidates(
    dataframe: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    candidates = dataframe.copy()

    candidates["dimension"] = dimension
    candidates["value"] = candidates[dimension]

    return candidates[
        [
            "dimension",
            "value",
            "baseline_revenue",
            "comparison_revenue",
            "absolute_change",
            "percentage_change",
            "contribution_to_total_change",
        ]
    ]


def rank_observed_drivers(
    candidates: list[pd.DataFrame],
) -> list[DriverEvidence]:
    combined = pd.concat(
        candidates,
        ignore_index=True,
    )

    deteriorations = combined[combined["absolute_change"] < 0].copy()

    ranked = deteriorations.sort_values(
        "absolute_change",
        ascending=True,
    ).reset_index(drop=True)

    return [
        DriverEvidence(
            dimension=str(row.dimension),
            value=str(row.value),
            baseline_revenue=float(row.baseline_revenue),
            comparison_revenue=float(row.comparison_revenue),
            absolute_change=float(row.absolute_change),
            percentage_change=float(row.percentage_change),
            contribution_to_total_change=float(row.contribution_to_total_change),
        )
        for row in ranked.itertuples(index=False)
    ]
