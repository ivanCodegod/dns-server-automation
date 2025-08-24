from typing import Any

from .collector import BaseMetricCollector


class NetworkMetricsManager:
    """Aggregates multiple collectors."""

    def __init__(self, collectors: list[BaseMetricCollector] | None = None):
        self.collectors = collectors or []

    def start_all(self, **kwargs) -> None:
        for c in self.collectors:
            c.start(**kwargs)

    def stop_all(self, **kwargs) -> None:
        for c in self.collectors:
            c.stop(**kwargs)

    def get_all(self) -> dict[str, Any]:
        result = {}
        for c in self.collectors:
            result[c.__class__.__name__] = c.get_metrics()
        return result
