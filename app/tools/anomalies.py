from datetime import date

import pandas as pd
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
)

from app.analytics.dimensions import (
    add_customer_dimensions,
    add_product_dimensions,
)
from app.analytics.revenue import (
    add_net_revenue,
    filter_period,
)
from app.ml.inference import (
    MLInferenceError,
    score_revenue_anomalies,
)
from app.ml.training import (
    MLInputError,
    MLTrainingError,
    train_revenue_anomaly_model,
)
from app.tools.base import BaseTool
from app.tools.contracts import (
    ToolCall,
    ToolDefinition,
    ToolResult,
)
from app.tools.errors import ToolExecutionError

DEFAULT_ANOMALY_DIMENSIONS = [
    "region",
    "segment",
    "category",
    "sales_channel",
]


class AnomalyDetectionArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    baseline_start: date
    baseline_end: date
    comparison_start: date
    comparison_end: date

    dimensions: list[str] = Field(
        default_factory=lambda: DEFAULT_ANOMALY_DIMENSIONS.copy(),
        min_length=1,
    )

    contamination: float = Field(
        default=0.08,
        gt=0.0,
        le=0.5,
    )

    random_state: int = 42

    max_anomalies: int = Field(
        default=10,
        ge=0,
    )


class AnomalyDetectionTool(BaseTool):
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
            name="detect_revenue_anomalies",
            description=(
                "Detect unusual revenue behavior in a comparison "
                "period using anomaly models trained only on the "
                "baseline period. Anomalies indicate unusual "
                "behavior and do not establish causality."
            ),
            input_schema=(AnomalyDetectionArguments.model_json_schema()),
        )

    def _run(
        self,
        call: ToolCall,
    ) -> ToolResult:
        arguments = self._parse_arguments(call=call)

        self._validate_datasets()

        enriched_orders = self._build_enriched_orders()

        self._validate_dimensions(
            dataframe=enriched_orders,
            dimensions=arguments.dimensions,
        )

        baseline = filter_period(
            dataframe=enriched_orders,
            start_date=arguments.baseline_start,
            end_date=arguments.baseline_end,
        )

        comparison = filter_period(
            dataframe=enriched_orders,
            start_date=arguments.comparison_start,
            end_date=arguments.comparison_end,
        )

        if baseline.empty:
            raise ToolExecutionError("Baseline period contains no orders.")

        if comparison.empty:
            raise ToolExecutionError("Comparison period contains no orders.")

        try:
            trained_model = train_revenue_anomaly_model(
                dataframe=baseline,
                dimensions=arguments.dimensions,
                contamination=arguments.contamination,
                random_state=arguments.random_state,
            )

            ml_result = score_revenue_anomalies(
                trained_model=trained_model,
                dataframe=comparison,
            )
        except (
            MLInputError,
            MLTrainingError,
            MLInferenceError,
        ) as exc:
            raise ToolExecutionError(str(exc)) from exc

        detected_anomalies = [
            anomaly for anomaly in ml_result.anomalies if anomaly.is_anomaly
        ]

        ranked_anomalies = sorted(
            detected_anomalies,
            key=lambda anomaly: anomaly.anomaly_score,
            reverse=True,
        )

        selected_anomalies = ranked_anomalies[: arguments.max_anomalies]

        anomalies = [
            {
                "date": anomaly.date,
                "dimension": anomaly.dimension,
                "value": anomaly.value,
                "daily_revenue": anomaly.daily_revenue,
                "anomaly_score": anomaly.anomaly_score,
                "is_anomaly": anomaly.is_anomaly,
            }
            for anomaly in selected_anomalies
        ]

        return ToolResult(
            tool_name=self.definition.name,
            success=True,
            output={
                "anomalies": anomalies,
                "anomaly_count": len(anomalies),
            },
        )

    def _parse_arguments(
        self,
        call: ToolCall,
    ) -> AnomalyDetectionArguments:
        try:
            arguments = AnomalyDetectionArguments.model_validate(call.arguments)
        except ValidationError as exc:
            raise ToolExecutionError(
                "Invalid detect_revenue_anomalies arguments."
            ) from exc

        if arguments.baseline_start > arguments.baseline_end:
            raise ToolExecutionError(
                "baseline_start must be before or equal to baseline_end."
            )

        if arguments.comparison_start > arguments.comparison_end:
            raise ToolExecutionError(
                "comparison_start must be before or equal to comparison_end."
            )

        normalized_dimensions = []

        for dimension in arguments.dimensions:
            normalized = dimension.strip()

            if not normalized:
                raise ToolExecutionError("dimensions must not contain empty values.")

            if normalized not in normalized_dimensions:
                normalized_dimensions.append(normalized)

        arguments.dimensions = normalized_dimensions

        return arguments

    def _build_enriched_orders(
        self,
    ) -> pd.DataFrame:
        orders = add_net_revenue(dataframe=self._orders)

        orders = add_customer_dimensions(
            orders,
            self._customers,
        )

        return add_product_dimensions(
            orders,
            self._products,
        )

    def _validate_datasets(
        self,
    ) -> None:
        if self._orders.empty:
            raise ToolExecutionError("Orders data must not be empty.")

        if self._customers.empty:
            raise ToolExecutionError("Customers data must not be empty.")

        if self._products.empty:
            raise ToolExecutionError("Products data must not be empty.")

    def _validate_dimensions(
        self,
        dataframe: pd.DataFrame,
        dimensions: list[str],
    ) -> None:
        missing_dimensions = [
            dimension for dimension in dimensions if dimension not in dataframe.columns
        ]

        if missing_dimensions:
            formatted_dimensions = ", ".join(sorted(missing_dimensions))

            raise ToolExecutionError(
                f"Unknown anomaly dimensions: {formatted_dimensions}."
            )
