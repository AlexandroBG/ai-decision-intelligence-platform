import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_numeric_dtype


def profile_dataframe(dataframe: pd.DataFrame) -> dict[str, object]:
    numeric_ranges = {}
    date_ranges = {}

    for column in dataframe.columns:
        if is_numeric_dtype(dataframe[column]):
            numeric_ranges[column] = {
                "min": dataframe[column].min(),
                "max": dataframe[column].max(),
            }

        if is_datetime64_any_dtype(dataframe[column]):
            date_ranges[column] = {
                "min": dataframe[column].min(),
                "max": dataframe[column].max(),
            }

    return {
        "rows": len(dataframe),
        "columns": len(dataframe.columns),
        "null_counts": dataframe.isna().sum().to_dict(),
        "duplicate_rows": int(dataframe.duplicated().sum()),
        "unique_counts": dataframe.nunique().to_dict(),
        "numeric_ranges": numeric_ranges,
        "date_ranges": date_ranges,
    }
