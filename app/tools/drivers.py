from datetime import date

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)

from app.analytics.engine import analyze_revenue_change
from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError


class DriverAnalysisArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    baseline_start: date
    baseline_end: date
    comparison_start: date
    comparison_end: date
    max_drivers: int = Field(
        default=5,
        ge=0,
    )


class DriverAnalysisTool(BaseTool):
    def __init__(
        self,
        orders: pd.DataFrame,
        customers: pd.DataFrame,
        products: pd.DataFrame,
    ) -> None:
        self._orders = orders.copy()
        self._customers = customers.copy()
        self._products = products.copy()

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="analyze_revenue_drivers",
            description=(
                "Identify the largest observed revenue "
                "deteriorations across business dimensions. "
                "Drivers represent observed contribution, "
                "not causal attribution."
            ),
            input_schema=(DriverAnalysisArguments.model_json_schema()),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        arguments = self._parse_arguments(call=call)

        self._validate_datasets()

        try:
            analytics_result = analyze_revenue_change(
                orders=self._orders,
                customers=self._customers,
                products=self._products,
                baseline_start=(arguments.baseline_start.isoformat()),
                baseline_end=(arguments.baseline_end.isoformat()),
                comparison_start=(arguments.comparison_start.isoformat()),
                comparison_end=(arguments.comparison_end.isoformat()),
            )
        except ValueError as exc:
            raise ToolExecutionError(str(exc)) from exc

        selected_drivers = analytics_result.drivers[: arguments.max_drivers]

        drivers = [
            {
                "dimension": driver.dimension,
                "value": driver.value,
                "baseline_revenue": (driver.baseline_revenue),
                "comparison_revenue": (driver.comparison_revenue),
                "absolute_change": (driver.absolute_change),
                "percentage_change": (driver.percentage_change),
                "contribution_to_total_change": (driver.contribution_to_total_change),
            }
            for driver in selected_drivers
        ]

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "drivers": drivers,
                "driver_count": len(drivers),
            },
        )

    def _parse_arguments(
        self,
        call: ToolCall,
    ) -> DriverAnalysisArguments:
        try:
            arguments = DriverAnalysisArguments.model_validate(call.arguments)
        except ValidationError as exc:
            raise ToolExecutionError(
                "Invalid analyze_revenue_drivers arguments."
            ) from exc

        if arguments.baseline_start > arguments.baseline_end:
            raise ToolExecutionError(
                "baseline_start must be before or equal to baseline_end."
            )

        if arguments.comparison_start > arguments.comparison_end:
            raise ToolExecutionError(
                "comparison_start must be before or equal to comparison_end."
            )

        return arguments

    def _validate_datasets(
        self,
    ) -> None:
        if self._orders.empty:
            raise ToolExecutionError("Orders data must not be empty.")

        if self._customers.empty:
            raise ToolExecutionError("Customers data must not be empty.")

        if self._products.empty:
            raise ToolExecutionError("Products data must not be empty.")
