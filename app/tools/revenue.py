from datetime import date

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
)

from app.analytics.revenue import (
    add_net_revenue,
    compare_revenue_periods,
    filter_period,
)
from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError

REQUIRED_REVENUE_COLUMNS = {
    "order_date",
    "quantity",
    "unit_price",
    "discount",
}


class RevenueAnalysisArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    baseline_start: date
    baseline_end: date
    comparison_start: date
    comparison_end: date


class RevenueAnalysisTool(BaseTool):
    def __init__(
        self,
        orders: pd.DataFrame,
    ) -> None:
        self._orders = orders.copy()

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="analyze_revenue",
            description=(
                "Compare total revenue between a baseline "
                "period and a comparison period."
            ),
            input_schema=(RevenueAnalysisArguments.model_json_schema()),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        arguments = self._parse_arguments(call=call)

        self._validate_orders()

        enriched_orders = add_net_revenue(dataframe=self._orders)

        baseline_orders = filter_period(
            dataframe=enriched_orders,
            start_date=arguments.baseline_start,
            end_date=arguments.baseline_end,
        )

        comparison_orders = filter_period(
            dataframe=enriched_orders,
            start_date=arguments.comparison_start,
            end_date=arguments.comparison_end,
        )

        if baseline_orders.empty:
            raise ToolExecutionError("Baseline period contains no orders.")

        if comparison_orders.empty:
            raise ToolExecutionError("Comparison period contains no orders.")

        comparison = compare_revenue_periods(
            baseline_orders,
            comparison_orders,
        )

        output = {
            "baseline_revenue": comparison.baseline_revenue,
            "comparison_revenue": comparison.comparison_revenue,
            "absolute_change": comparison.absolute_change,
            "percentage_change": comparison.percentage_change,
        }

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output=output,
        )

    def _parse_arguments(
        self,
        call: ToolCall,
    ) -> RevenueAnalysisArguments:
        try:
            arguments = RevenueAnalysisArguments.model_validate(call.arguments)
        except ValidationError as exc:
            raise ToolExecutionError("Invalid analyze_revenue arguments.") from exc

        if arguments.baseline_start > arguments.baseline_end:
            raise ToolExecutionError(
                "baseline_start must be before or equal to baseline_end."
            )

        if arguments.comparison_start > arguments.comparison_end:
            raise ToolExecutionError(
                "comparison_start must be before or equal to comparison_end."
            )

        return arguments

    def _validate_orders(
        self,
    ) -> None:
        missing_columns = REQUIRED_REVENUE_COLUMNS - set(self._orders.columns)

        if missing_columns:
            formatted_columns = ", ".join(sorted(missing_columns))

            raise ToolExecutionError(
                f"Orders data is missing required columns: {formatted_columns}."
            )
