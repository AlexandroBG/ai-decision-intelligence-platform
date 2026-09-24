import pytest

from app.observability.metrics import (
    METRIC_NAMES,
    MetricsRegistry,
)


def test_metrics_start_at_zero() -> None:
    registry = MetricsRegistry()

    snapshot = registry.snapshot()

    assert set(snapshot) == set(METRIC_NAMES)

    assert all(value == 0 for value in snapshot.values())


def test_metric_can_be_incremented() -> None:
    registry = MetricsRegistry()

    registry.increment("requests_total")

    registry.increment("requests_total")

    assert registry.snapshot()["requests_total"] == 2


def test_metric_increment_accepts_amount() -> None:
    registry = MetricsRegistry()

    registry.increment(
        "tool_calls_total",
        amount=3,
    )

    assert registry.snapshot()["tool_calls_total"] == 3


def test_unknown_metric_is_rejected() -> None:
    registry = MetricsRegistry()

    with pytest.raises(
        ValueError,
        match="Unknown metric",
    ):
        registry.increment("does_not_exist")


def test_negative_increment_is_rejected() -> None:
    registry = MetricsRegistry()

    with pytest.raises(
        ValueError,
        match=("Metric increment must not be negative"),
    ):
        registry.increment(
            "requests_total",
            amount=-1,
        )


def test_metrics_can_be_reset() -> None:
    registry = MetricsRegistry()

    registry.increment("requests_total")

    registry.increment(
        "llm_calls_total",
        amount=2,
    )

    registry.reset()

    assert all(value == 0 for value in registry.snapshot().values())
