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
