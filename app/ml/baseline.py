import pandas as pd


def add_statistical_anomaly_scores(
    dataframe: pd.DataFrame,
    window: int = 7,
    min_periods: int = 3,
    threshold: float = 2.0,
) -> pd.DataFrame:
    required_columns = {
        "date",
        "dimension",
        "value",
        "daily_revenue",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns for anomaly detection: {missing}")

    if window <= 0:
        raise ValueError("Window must be greater than zero.")

    if min_periods <= 0:
        raise ValueError("min_periods must be greater than zero.")

    if min_periods > window:
        raise ValueError("min_periods must be less than or equal to window.")

    if threshold <= 0:
        raise ValueError("Threshold must be greater than zero.")

    result = dataframe.copy()

    result = result.sort_values(
        [
            "dimension",
            "value",
            "date",
        ]
    ).reset_index(drop=True)

    group_columns = [
        "dimension",
        "value",
    ]

    historical_revenue = result.groupby(group_columns)["daily_revenue"].shift(1)

    result["expected_revenue"] = (
        historical_revenue.groupby(
            [
                result["dimension"],
                result["value"],
            ]
        )
        .rolling(
            window=window,
            min_periods=min_periods,
        )
        .mean()
        .reset_index(
            level=[0, 1],
            drop=True,
        )
    )

    result["historical_std"] = (
        historical_revenue.groupby(
            [
                result["dimension"],
                result["value"],
            ]
        )
        .rolling(
            window=window,
            min_periods=min_periods,
        )
        .std()
        .reset_index(
            level=[0, 1],
            drop=True,
        )
    )

    valid_std = result["historical_std"].notna() & (result["historical_std"] > 0)

    result["z_score"] = pd.NA

    result.loc[
        valid_std,
        "z_score",
    ] = (
        result.loc[
            valid_std,
            "daily_revenue",
        ]
        - result.loc[
            valid_std,
            "expected_revenue",
        ]
    ) / result.loc[
        valid_std,
        "historical_std",
    ]

    result["is_anomaly"] = False

    result.loc[
        valid_std,
        "is_anomaly",
    ] = (
        result.loc[
            valid_std,
            "z_score",
        ]
        .abs()
        .astype(float)
        >= threshold
    )

    return result
