import pandas as pd
import pytest

from app.ml.features import (
    FEATURE_COLUMNS,
    build_daily_revenue_features,
    build_daily_revenue_features_for_dimensions,
)


def build_test_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "O001",
                "O002",
                "O003",
                "O004",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-01 10:00:00",
                    "2025-07-01 14:00:00",
                    "2025-07-02 09:00:00",
                    "2025-07-01 11:00:00",
                ]
            ),
            "region": [
                "South",
                "South",
                "South",
                "North",
            ],
            "category": [
                "Computing",
                "Computing",
                "Office",
                "Office",
            ],
            "quantity": [
                1,
                2,
                3,
                4,
            ],
            "discount": [
                0.10,
                0.20,
                0.05,
                0.15,
            ],
            "net_revenue": [
                100.0,
                150.0,
                200.0,
                300.0,
            ],
        }
    )


def test_build_daily_features_aggregates_business_metrics() -> None:
    result = build_daily_revenue_features(
        dataframe=build_test_dataframe(),
        dimension="region",
    )

    south_july_first = result[
        (result["value"] == "South") & (result["date"] == pd.Timestamp("2025-07-01"))
    ].iloc[0]

    assert south_july_first["daily_revenue"] == 250.0

    assert south_july_first["order_count"] == 2

    assert south_july_first["units_sold"] == 3

    assert south_july_first["average_order_value"] == 125.0

    assert south_july_first["average_discount"] == pytest.approx(0.15)


def test_build_daily_features_uses_standard_columns() -> None:
    result = build_daily_revenue_features(
        dataframe=build_test_dataframe(),
        dimension="region",
    )

    assert result.columns.tolist() == [
        "date",
        "dimension",
        "value",
        *FEATURE_COLUMNS,
    ]


def test_build_daily_features_rejects_missing_dimension() -> None:
    with pytest.raises(
        ValueError,
        match="Missing required columns",
    ):
        build_daily_revenue_features(
            dataframe=build_test_dataframe(),
            dimension="segment",
        )


def test_build_daily_features_for_multiple_dimensions() -> None:
    result = build_daily_revenue_features_for_dimensions(
        dataframe=build_test_dataframe(),
        dimensions=[
            "region",
            "category",
        ],
    )

    assert set(result["dimension"]) == {
        "region",
        "category",
    }

    assert "South" in set(result["value"])

    assert "Computing" in set(result["value"])
