import pandas as pd

from app.tools.anomalies import AnomalyDetectionTool
from app.tools.drivers import DriverAnalysisTool
from app.tools.revenue import RevenueAnalysisTool


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": ["o1"],
            "customer_id": ["c1"],
            "product_id": ["p1"],
            "order_date": pd.to_datetime(["2025-07-01"]),
            "quantity": [1],
            "unit_price": [100.0],
            "discount": [0.0],
            "sales_channel": ["Web"],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": ["c1"],
            "signup_date": pd.to_datetime(["2024-01-01"]),
            "segment": ["SMB"],
            "region": ["South"],
            "acquisition_channel": ["Organic"],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": ["p1"],
            "product_name": ["Laptop"],
            "category": ["Computing"],
            "unit_cost": [60.0],
        }
    )


def test_revenue_tool_exposes_input_schema() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    schema = tool.definition.input_schema

    assert schema["type"] == "object"

    assert set(schema["properties"]) == {
        "baseline_start",
        "baseline_end",
        "comparison_start",
        "comparison_end",
    }


def test_revenue_dates_are_exposed_as_date_strings() -> None:
    tool = RevenueAnalysisTool(orders=build_orders())

    schema = tool.definition.input_schema

    baseline_start = schema["properties"]["baseline_start"]

    assert baseline_start["type"] == "string"

    assert baseline_start["format"] == "date"


def test_driver_tool_exposes_max_drivers() -> None:
    tool = DriverAnalysisTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    schema = tool.definition.input_schema

    assert "max_drivers" in schema["properties"]

    max_drivers = schema["properties"]["max_drivers"]

    assert max_drivers["default"] == 5

    assert max_drivers["minimum"] == 0


def test_anomaly_tool_exposes_dimensions() -> None:
    tool = AnomalyDetectionTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    schema = tool.definition.input_schema

    assert "dimensions" in schema["properties"]

    dimensions = schema["properties"]["dimensions"]

    assert dimensions["type"] == "array"


def test_anomaly_tool_exposes_contamination_constraints() -> None:
    tool = AnomalyDetectionTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    schema = tool.definition.input_schema

    contamination = schema["properties"]["contamination"]

    assert contamination["default"] == 0.08

    assert contamination["exclusiveMinimum"] == 0.0

    assert contamination["maximum"] == 0.5


def test_anomaly_tool_exposes_max_anomalies() -> None:
    tool = AnomalyDetectionTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )

    schema = tool.definition.input_schema

    max_anomalies = schema["properties"]["max_anomalies"]

    assert max_anomalies["default"] == 10

    assert max_anomalies["minimum"] == 0
