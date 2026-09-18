import pandas as pd

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
from app.ml.inference import score_revenue_anomalies
from app.ml.training import train_revenue_anomaly_model


def build_enriched_orders() -> pd.DataFrame:
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


def build_training_period() -> pd.DataFrame:
    return filter_period(
        dataframe=build_enriched_orders(),
        start_date="2025-07-01",
        end_date="2025-07-31",
    )


def build_comparison_period() -> pd.DataFrame:
    return filter_period(
        dataframe=build_enriched_orders(),
        start_date="2025-08-01",
        end_date="2025-08-31",
    )


def train_scenario_model():
    return train_revenue_anomaly_model(
        dataframe=build_training_period(),
        dimensions=[
            "region",
            "segment",
            "category",
            "sales_channel",
        ],
        contamination=0.1,
        random_state=42,
    )


def test_training_features_use_only_baseline_period() -> None:
    trained_model = train_scenario_model()

    assert not trained_model.features.empty

    assert trained_model.features["date"].min() >= pd.Timestamp("2025-07-01")

    assert trained_model.features["date"].max() <= pd.Timestamp("2025-07-31")


def test_inference_evidence_uses_only_comparison_period() -> None:
    trained_model = train_scenario_model()

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_comparison_period(),
    )

    dates = pd.to_datetime([anomaly.date for anomaly in result.anomalies])

    assert dates.min() >= pd.Timestamp("2025-08-01")

    assert dates.max() <= pd.Timestamp("2025-08-31")


def test_comparison_period_contains_detected_anomalies() -> None:
    trained_model = train_scenario_model()

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_comparison_period(),
    )

    detected = [anomaly for anomaly in result.anomalies if anomaly.is_anomaly]

    assert detected


def test_south_region_receives_ml_anomaly_evidence() -> None:
    trained_model = train_scenario_model()

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_comparison_period(),
    )

    south_anomalies = [
        anomaly
        for anomaly in result.anomalies
        if anomaly.dimension == "region"
        and anomaly.value == "South"
        and anomaly.is_anomaly
    ]

    assert south_anomalies


def test_expected_scenario_slices_are_scored() -> None:
    trained_model = train_scenario_model()

    result = score_revenue_anomalies(
        trained_model=trained_model,
        dataframe=build_comparison_period(),
    )

    observed_pairs = {
        (
            anomaly.dimension,
            anomaly.value,
        )
        for anomaly in result.anomalies
    }

    assert ("region", "South") in observed_pairs
    assert ("category", "Computing") in observed_pairs
    assert ("sales_channel", "Partner") in observed_pairs
