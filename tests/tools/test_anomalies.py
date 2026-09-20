import pandas as pd

from app.ml.contracts import (
    AnomalyEvidence,
    MLResult,
)
from app.tools.anomalies import (
    AnomalyDetectionTool,
)
from app.tools.contracts import ToolCall


def build_orders() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "order_id": [
                "o1",
                "o2",
                "o3",
                "o4",
            ],
            "customer_id": [
                "c1",
                "c2",
                "c1",
                "c2",
            ],
            "product_id": [
                "p1",
                "p2",
                "p1",
                "p2",
            ],
            "order_date": pd.to_datetime(
                [
                    "2025-07-10",
                    "2025-07-20",
                    "2025-08-10",
                    "2025-08-20",
                ]
            ),
            "quantity": [
                2,
                1,
                1,
                1,
            ],
            "unit_price": [
                100.0,
                200.0,
                100.0,
                100.0,
            ],
            "discount": [
                0.0,
                0.0,
                0.0,
                0.0,
            ],
            "sales_channel": [
                "Partner",
                "Web",
                "Partner",
                "Web",
            ],
        }
    )


def build_customers() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "customer_id": [
                "c1",
                "c2",
            ],
            "signup_date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-02-01",
                ]
            ),
            "segment": [
                "Enterprise",
                "SMB",
            ],
            "region": [
                "South",
                "North",
            ],
            "acquisition_channel": [
                "Organic",
                "Paid",
            ],
        }
    )


def build_products() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "product_id": [
                "p1",
                "p2",
            ],
            "product_name": [
                "Laptop",
                "Router",
            ],
            "category": [
                "Computing",
                "Networking",
            ],
            "unit_cost": [
                60.0,
                120.0,
            ],
        }
    )


def build_tool() -> AnomalyDetectionTool:
    return AnomalyDetectionTool(
        orders=build_orders(),
        customers=build_customers(),
        products=build_products(),
    )


def build_valid_call() -> ToolCall:
    return ToolCall(
        tool_name="detect_revenue_anomalies",
        arguments={
            "baseline_start": "2025-07-01",
            "baseline_end": "2025-07-31",
            "comparison_start": "2025-08-01",
            "comparison_end": "2025-08-31",
        },
    )


def test_anomaly_tool_exposes_definition() -> None:
    tool = build_tool()

    assert tool.definition.name == "detect_revenue_anomalies"

    assert "do not establish causality" in tool.definition.description


def test_anomaly_tool_returns_ranked_anomalies(
    monkeypatch,
) -> None:
    tool = build_tool()

    captured = {}

    def fake_train(
        dataframe,
        dimensions,
        contamination,
        random_state,
    ):
        captured["training_dates"] = set(dataframe["order_date"].dt.month)

        captured["dimensions"] = dimensions
        captured["contamination"] = contamination
        captured["random_state"] = random_state

        return object()

    def fake_score(
        trained_model,
        dataframe,
    ):
        captured["inference_dates"] = set(dataframe["order_date"].dt.month)

        return MLResult(
            anomalies=[
                AnomalyEvidence(
                    date="2025-08-10",
                    dimension="region",
                    value="South",
                    daily_revenue=40.0,
                    anomaly_score=0.24,
                    is_anomaly=True,
                ),
                AnomalyEvidence(
                    date="2025-08-12",
                    dimension="category",
                    value="Computing",
                    daily_revenue=35.0,
                    anomaly_score=0.19,
                    is_anomaly=True,
                ),
                AnomalyEvidence(
                    date="2025-08-15",
                    dimension="sales_channel",
                    value="Partner",
                    daily_revenue=30.0,
                    anomaly_score=0.14,
                    is_anomaly=True,
                ),
                AnomalyEvidence(
                    date="2025-08-16",
                    dimension="region",
                    value="North",
                    daily_revenue=200.0,
                    anomaly_score=-0.05,
                    is_anomaly=False,
                ),
            ]
        )

    monkeypatch.setattr(
        "app.tools.anomalies.train_revenue_anomaly_model",
        fake_train,
    )

    monkeypatch.setattr(
        "app.tools.anomalies.score_revenue_anomalies",
        fake_score,
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is True

    assert captured["training_dates"] == {7}

    assert captured["inference_dates"] == {8}

    assert captured["dimensions"] == [
        "region",
        "segment",
        "category",
        "sales_channel",
    ]

    assert captured["contamination"] == 0.08

    assert captured["random_state"] == 42

    assert result.output["anomaly_count"] == 3

    assert [anomaly["anomaly_score"] for anomaly in result.output["anomalies"]] == [
        0.24,
        0.19,
        0.14,
    ]


def test_anomaly_tool_keeps_only_detected_anomalies(
    monkeypatch,
) -> None:
    tool = build_tool()

    monkeypatch.setattr(
        "app.tools.anomalies.train_revenue_anomaly_model",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        "app.tools.anomalies.score_revenue_anomalies",
        lambda **kwargs: MLResult(
            anomalies=[
                AnomalyEvidence(
                    date="2025-08-10",
                    dimension="region",
                    value="South",
                    daily_revenue=40.0,
                    anomaly_score=0.2,
                    is_anomaly=True,
                ),
                AnomalyEvidence(
                    date="2025-08-11",
                    dimension="region",
                    value="North",
                    daily_revenue=100.0,
                    anomaly_score=-0.1,
                    is_anomaly=False,
                ),
            ]
        ),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is True

    assert result.output["anomaly_count"] == 1

    assert result.output["anomalies"][0]["value"] == "South"


def test_anomaly_tool_respects_max_anomalies(
    monkeypatch,
) -> None:
    tool = build_tool()

    monkeypatch.setattr(
        "app.tools.anomalies.train_revenue_anomaly_model",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        "app.tools.anomalies.score_revenue_anomalies",
        lambda **kwargs: MLResult(
            anomalies=[
                AnomalyEvidence(
                    date="2025-08-10",
                    dimension="region",
                    value="South",
                    daily_revenue=40.0,
                    anomaly_score=0.3,
                    is_anomaly=True,
                ),
                AnomalyEvidence(
                    date="2025-08-11",
                    dimension="category",
                    value="Computing",
                    daily_revenue=30.0,
                    anomaly_score=0.2,
                    is_anomaly=True,
                ),
            ]
        ),
    )

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "max_anomalies": 1,
            },
        )
    )

    assert result.success is True

    assert result.output["anomaly_count"] == 1

    assert result.output["anomalies"][0]["anomaly_score"] == 0.3


def test_anomaly_tool_allows_zero_max_anomalies(
    monkeypatch,
) -> None:
    tool = build_tool()

    monkeypatch.setattr(
        "app.tools.anomalies.train_revenue_anomaly_model",
        lambda **kwargs: object(),
    )

    monkeypatch.setattr(
        "app.tools.anomalies.score_revenue_anomalies",
        lambda **kwargs: MLResult(
            anomalies=[
                AnomalyEvidence(
                    date="2025-08-10",
                    dimension="region",
                    value="South",
                    daily_revenue=40.0,
                    anomaly_score=0.3,
                    is_anomaly=True,
                )
            ]
        ),
    )

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "max_anomalies": 0,
            },
        )
    )

    assert result.success is True

    assert result.output == {
        "anomalies": [],
        "anomaly_count": 0,
    }


def test_anomaly_tool_rejects_invalid_arguments() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "bad-date",
            },
        )
    )

    assert result.success is False

    assert result.error == ("Invalid detect_revenue_anomalies arguments.")


def test_anomaly_tool_rejects_extra_arguments() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "unexpected_argument": True,
            },
        )
    )

    assert result.success is False

    assert result.error == ("Invalid detect_revenue_anomalies arguments.")


def test_anomaly_tool_rejects_invalid_baseline_period() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-31",
                "baseline_end": "2025-07-01",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
            },
        )
    )

    assert result.success is False

    assert result.error == ("baseline_start must be before or equal to baseline_end.")


def test_anomaly_tool_rejects_invalid_comparison_period() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-31",
                "comparison_end": "2025-08-01",
            },
        )
    )

    assert result.success is False

    assert result.error == (
        "comparison_start must be before or equal to comparison_end."
    )


def test_anomaly_tool_rejects_unknown_dimension() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "dimensions": [
                    "region",
                    "missing_dimension",
                ],
            },
        )
    )

    assert result.success is False

    assert result.error == ("Unknown anomaly dimensions: missing_dimension.")


def test_anomaly_tool_normalizes_dimensions(
    monkeypatch,
) -> None:
    tool = build_tool()

    captured = {}

    def fake_train(
        dataframe,
        dimensions,
        contamination,
        random_state,
    ):
        captured["dimensions"] = dimensions
        return object()

    monkeypatch.setattr(
        "app.tools.anomalies.train_revenue_anomaly_model",
        fake_train,
    )

    monkeypatch.setattr(
        "app.tools.anomalies.score_revenue_anomalies",
        lambda **kwargs: MLResult(anomalies=[]),
    )

    result = tool.execute(
        call=ToolCall(
            tool_name="detect_revenue_anomalies",
            arguments={
                "baseline_start": "2025-07-01",
                "baseline_end": "2025-07-31",
                "comparison_start": "2025-08-01",
                "comparison_end": "2025-08-31",
                "dimensions": [
                    " region ",
                    "region",
                    " category ",
                ],
            },
        )
    )

    assert result.success is True

    assert captured["dimensions"] == [
        "region",
        "category",
    ]


def test_anomaly_tool_rejects_empty_orders() -> None:
    tool = AnomalyDetectionTool(
        orders=pd.DataFrame(),
        customers=build_customers(),
        products=build_products(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Orders data must not be empty."


def test_anomaly_tool_rejects_empty_customers() -> None:
    tool = AnomalyDetectionTool(
        orders=build_orders(),
        customers=pd.DataFrame(),
        products=build_products(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Customers data must not be empty."


def test_anomaly_tool_rejects_empty_products() -> None:
    tool = AnomalyDetectionTool(
        orders=build_orders(),
        customers=build_customers(),
        products=pd.DataFrame(),
    )

    result = tool.execute(call=build_valid_call())

    assert result.success is False

    assert result.error == "Products data must not be empty."


def test_anomaly_tool_rejects_wrong_tool_name() -> None:
    tool = build_tool()

    result = tool.execute(
        call=ToolCall(
            tool_name="wrong_tool",
        )
    )

    assert result.success is False

    assert result.error is not None

    assert "does not match tool definition" in result.error
