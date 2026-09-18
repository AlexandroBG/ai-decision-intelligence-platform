import pandas as pd


def add_customer_dimensions(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
) -> pd.DataFrame:
    customer_dimensions = customers[
        [
            "customer_id",
            "segment",
            "region",
        ]
    ]

    return orders.merge(
        customer_dimensions,
        on="customer_id",
        how="left",
        validate="many_to_one",
    )


def aggregate_revenue_by_dimension(
    dataframe: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    return (
        dataframe.groupby(dimension, as_index=False)["net_revenue"]
        .sum()
        .sort_values("net_revenue", ascending=False)
        .reset_index(drop=True)
    )


def compare_revenue_by_dimension(
    baseline: pd.DataFrame,
    comparison: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    baseline_summary = aggregate_revenue_by_dimension(
        dataframe=baseline,
        dimension=dimension,
    ).rename(
        columns={
            "net_revenue": "baseline_revenue",
        }
    )

    comparison_summary = aggregate_revenue_by_dimension(
        dataframe=comparison,
        dimension=dimension,
    ).rename(
        columns={
            "net_revenue": "comparison_revenue",
        }
    )

    result = baseline_summary.merge(
        comparison_summary,
        on=dimension,
        how="outer",
    ).fillna(0.0)

    result["absolute_change"] = (
        result["comparison_revenue"] - result["baseline_revenue"]
    )

    result["percentage_change"] = 0.0

    nonzero_baseline = result["baseline_revenue"] != 0

    result.loc[
        nonzero_baseline,
        "percentage_change",
    ] = (
        result.loc[
            nonzero_baseline,
            "absolute_change",
        ]
        / result.loc[
            nonzero_baseline,
            "baseline_revenue",
        ]
    )

    return result.sort_values("absolute_change").reset_index(drop=True)


def add_product_dimensions(
    orders: pd.DataFrame,
    products: pd.DataFrame,
) -> pd.DataFrame:
    product_dimensions = products[
        [
            "product_id",
            "category",
        ]
    ]

    return orders.merge(
        product_dimensions,
        on="product_id",
        how="left",
        validate="many_to_one",
    )


def add_change_contribution(
    dataframe: pd.DataFrame,
    total_change: float,
) -> pd.DataFrame:
    result = dataframe.copy()

    if total_change == 0:
        result["contribution_to_total_change"] = 0.0
        return result

    result["contribution_to_total_change"] = result["absolute_change"] / total_change

    return result
