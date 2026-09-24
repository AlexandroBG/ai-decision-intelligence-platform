from threading import Lock

METRIC_NAMES = (
    "requests_total",
    "provider_errors_total",
    "agent_completed_total",
    "agent_failed_total",
    "tool_calls_total",
    "llm_calls_total",
)


class MetricsRegistry:
    def __init__(
        self,
    ) -> None:
        self._lock = Lock()

        self._counters = {name: 0 for name in METRIC_NAMES}

    def increment(
        self,
        name: str,
        amount: int = 1,
    ) -> None:
        if name not in self._counters:
            raise ValueError(f"Unknown metric: {name}")

        if amount < 0:
            raise ValueError("Metric increment must not be negative.")

        with self._lock:
            self._counters[name] += amount

    def snapshot(
        self,
    ) -> dict[str, int]:
        with self._lock:
            return dict(self._counters)

    def reset(
        self,
    ) -> None:
        with self._lock:
            for name in self._counters:
                self._counters[name] = 0


metrics = MetricsRegistry()
