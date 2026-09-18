import pandas as pd

FEATURE_COLUMNS = [
    "daily_revenue",
    "order_count",
    "units_sold",
    "average_order_value",
    "average_discount",
]


def build_daily_revenue_features(
    dataframe: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    required_columns = {
        "order_id",
        "order_date",
        "quantity",
        "discount",
        "net_revenue",
        dimension,
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns for feature generation: {missing}")

    features = dataframe.copy()

    features["date"] = features["order_date"].dt.normalize()

    daily = features.groupby(
        [
            "date",
            dimension,
        ],
        as_index=False,
    ).agg(
        daily_revenue=(
            "net_revenue",
            "sum",
        ),
        order_count=(
            "order_id",
            "nunique",
        ),
        units_sold=(
            "quantity",
            "sum",
        ),
        average_discount=(
            "discount",
            "mean",
        ),
    )

    daily["average_order_value"] = daily["daily_revenue"] / daily["order_count"]

    daily = daily.rename(
        columns={
            dimension: "value",
        }
    )

    daily["dimension"] = dimension

    return (
        daily[
            [
                "date",
                "dimension",
                "value",
                *FEATURE_COLUMNS,
            ]
        ]
        .sort_values(
            [
                "value",
                "date",
            ]
        )
        .reset_index(drop=True)
    )


def build_daily_revenue_features_for_dimensions(
    dataframe: pd.DataFrame,
    dimensions: list[str],
) -> pd.DataFrame:
    feature_frames = [
        build_daily_revenue_features(
            dataframe=dataframe,
            dimension=dimension,
        )
        for dimension in dimensions
    ]

    if not feature_frames:
        return pd.DataFrame(
            columns=[
                "date",
                "dimension",
                "value",
                *FEATURE_COLUMNS,
            ]
        )

    return (
        pd.concat(
            feature_frames,
            ignore_index=True,
        )
        .sort_values(
            [
                "dimension",
                "value",
                "date",
            ]
        )
        .reset_index(drop=True)
    )
