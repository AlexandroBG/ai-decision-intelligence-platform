from app.analytics.dimensions import (
    add_customer_dimensions,
    add_product_dimensions,
)
from app.analytics.revenue import (
    add_net_revenue,
    filter_period,
)
from app.data.loaders import (
    load_customers,
    load_orders,
    load_products,
)
from app.ml.contracts import MLResult
from app.ml.inference import score_revenue_anomalies
from app.ml.persistence import (
    load_trained_model,
    save_trained_model,
)
from app.ml.training import train_revenue_anomaly_model


def build_enriched_orders():
    orders = add_net_revenue(load_orders())

    orders = add_customer_dimensions(
        orders=orders,
        customers=load_customers(),
    )

    orders = add_product_dimensions(
        orders=orders,
        products=load_products(),
    )

    return orders


def test_ml_pipeline_end_to_end(
    tmp_path,
) -> None:
    enriched = build_enriched_orders()

    july = filter_period(
        dataframe=enriched,
        start_date="2025-07-01",
        end_date="2025-07-31",
    )

    august = filter_period(
        dataframe=enriched,
        start_date="2025-08-01",
        end_date="2025-08-31",
    )

    trained_model = train_revenue_anomaly_model(
        dataframe=july,
        dimensions=[
            "region",
            "segment",
            "category",
            "sales_channel",
        ],
        contamination=0.08,
        random_state=42,
    )

    model_path = tmp_path / "decisionai_anomaly_model.joblib"

    save_trained_model(
        trained_model=trained_model,
        path=model_path,
    )

    loaded_model = load_trained_model(
        path=model_path,
    )

    result = score_revenue_anomalies(
        trained_model=loaded_model,
        dataframe=august,
    )

    assert isinstance(
        result,
        MLResult,
    )

    assert result.anomalies

    assert loaded_model.contamination == 0.08
    assert loaded_model.random_state == 42

    assert len(loaded_model.models) > 0


def test_ml_pipeline_detects_expected_scenario_signals(
    tmp_path,
) -> None:
    enriched = build_enriched_orders()

    july = filter_period(
        dataframe=enriched,
        start_date="2025-07-01",
        end_date="2025-07-31",
    )

    august = filter_period(
        dataframe=enriched,
        start_date="2025-08-01",
        end_date="2025-08-31",
    )

    trained_model = train_revenue_anomaly_model(
        dataframe=july,
        dimensions=[
            "region",
            "segment",
            "category",
            "sales_channel",
        ],
        contamination=0.08,
        random_state=42,
    )

    model_path = tmp_path / "decisionai_anomaly_model.joblib"

    save_trained_model(
        trained_model=trained_model,
        path=model_path,
    )

    loaded_model = load_trained_model(
        path=model_path,
    )

    result = score_revenue_anomalies(
        trained_model=loaded_model,
        dataframe=august,
    )

    detected_pairs = {
        (
            anomaly.dimension,
            anomaly.value,
        )
        for anomaly in result.anomalies
        if anomaly.is_anomaly
    }

    assert (
        "region",
        "South",
    ) in detected_pairs

    assert (
        "category",
        "Computing",
    ) in detected_pairs

    assert (
        "sales_channel",
        "Partner",
    ) in detected_pairs
