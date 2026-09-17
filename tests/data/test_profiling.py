import pandas as pd

from app.data.profiling import profile_dataframe


def test_profile_dataframe_reports_structure() -> None:
    dataframe = pd.DataFrame(
        {
            "id": ["A", "B", "B"],
            "value": [1, 2, 2],
        }
    )

    profile = profile_dataframe(dataframe)

    assert profile["rows"] == 3
    assert profile["columns"] == 2
    assert profile["null_counts"]["id"] == 0
    assert profile["duplicate_rows"] == 1
    assert profile["unique_counts"]["id"] == 2


def test_profile_dataframe_reports_numeric_ranges() -> None:
    dataframe = pd.DataFrame(
        {
            "quantity": [1, 3, 5],
        }
    )

    profile = profile_dataframe(dataframe)

    assert profile["numeric_ranges"]["quantity"]["min"] == 1
    assert profile["numeric_ranges"]["quantity"]["max"] == 5


def test_profile_dataframe_reports_date_ranges() -> None:
    dataframe = pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                [
                    "2025-07-01",
                    "2025-08-31",
                ]
            )
        }
    )

    profile = profile_dataframe(dataframe)

    assert profile["date_ranges"]["order_date"]["min"] == pd.Timestamp("2025-07-01")
    assert profile["date_ranges"]["order_date"]["max"] == pd.Timestamp("2025-08-31")
