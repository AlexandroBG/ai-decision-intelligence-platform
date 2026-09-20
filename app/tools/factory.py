import pandas as pd

from app.tools.anomalies import AnomalyDetectionTool
from app.tools.drivers import DriverAnalysisTool
from app.tools.registry import ToolRegistry
from app.tools.revenue import RevenueAnalysisTool


def build_default_tool_registry(
    orders: pd.DataFrame,
    customers: pd.DataFrame,
    products: pd.DataFrame,
) -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(
        RevenueAnalysisTool(
            orders=orders,
        )
    )

    registry.register(
        DriverAnalysisTool(
            orders=orders,
            customers=customers,
            products=products,
        )
    )

    registry.register(
        AnomalyDetectionTool(
            orders=orders,
            customers=customers,
            products=products,
        )
    )

    return registry
