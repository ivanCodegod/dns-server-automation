from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseMetricCollector(ABC):
    @abstractmethod
    def start(self, **kwargs) -> None:
        """Start collection."""

    @abstractmethod
    def stop(self, **kwargs) -> None:
        """Stop collection."""

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """Return collected metrics."""


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
