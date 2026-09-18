import pandas as pd

from app.analytics.dimensions import (
    add_change_contribution,
    add_customer_dimensions,
    add_product_dimensions,
    aggregate_revenue_by_dimension,
    compare_revenue_by_dimension,
)


def test_add_customer_dimensions() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O001", "O002"],
            "customer_id": ["C001", "C002"],
        }
    )

    customers = pd.DataFrame(
        {
            "customer_id": ["C001", "C002"],
            "segment": ["SMB", "Enterprise"],
            "region": ["South", "North"],
        }
    )

    result = add_customer_dimensions(
        orders=orders,
        customers=customers,
    )

    assert result["region"].tolist() == ["South", "North"]
    assert result["segment"].tolist() == ["SMB", "Enterprise"]


def test_aggregate_revenue_by_dimension() -> None:
    dataframe = pd.DataFrame(
        {
            "region": ["South", "South", "North"],
            "net_revenue": [100.0, 50.0, 200.0],
        }
    )

    result = aggregate_revenue_by_dimension(
        dataframe=dataframe,
        dimension="region",
    )

    assert result.to_dict("records") == [
        {
            "region": "North",
            "net_revenue": 200.0,
        },
        {
            "region": "South",
            "net_revenue": 150.0,
        },
    ]


def test_compare_revenue_by_dimension() -> None:
    baseline = pd.DataFrame(
        {
            "region": ["South", "North"],
            "net_revenue": [500.0, 300.0],
        }
    )

    comparison = pd.DataFrame(
        {
            "region": ["South", "North"],
            "net_revenue": [200.0, 270.0],
        }
    )

    result = compare_revenue_by_dimension(
        baseline=baseline,
        comparison=comparison,
        dimension="region",
    )

    south = result[result["region"] == "South"].iloc[0]

    assert south["baseline_revenue"] == 500.0
    assert south["comparison_revenue"] == 200.0
    assert south["absolute_change"] == -300.0
    assert south["percentage_change"] == -0.6


def test_add_product_dimensions() -> None:
    orders = pd.DataFrame(
        {
            "order_id": ["O001", "O002"],
            "product_id": ["P001", "P002"],
        }
    )

    products = pd.DataFrame(
        {
            "product_id": ["P001", "P002"],
            "category": ["Computing", "Office"],
        }
    )

    result = add_product_dimensions(
        orders=orders,
        products=products,
    )

    assert result["category"].tolist() == ["Computing", "Office"]


def test_add_change_contribution() -> None:
    dataframe = pd.DataFrame(
        {
            "region": ["South", "North"],
            "absolute_change": [-300.0, -100.0],
        }
    )

    result = add_change_contribution(
        dataframe=dataframe,
        total_change=-400.0,
    )

    south = result[result["region"] == "South"].iloc[0]
    north = result[result["region"] == "North"].iloc[0]

    assert south["contribution_to_total_change"] == 0.75
    assert north["contribution_to_total_change"] == 0.25
