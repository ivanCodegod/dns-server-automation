from pytest_check import check

from src.taf_core.metrics.collector import NetworkMetricsManager
from src.taf_core.metrics.types import PageLoadMetrics


class NetworkMetricsValidator:
    def __init__(self, metrics_mgr: NetworkMetricsManager):
        self.metrics_mgr = metrics_mgr

    def validate_page_load(self):
        for collector_name, metrics in self.metrics_mgr.get_all().items():
            self._validate_metrics(collector_name, metrics)

    def _validate_metrics(self, collector_name: str, metrics: PageLoadMetrics):
        check.is_true(metrics.total_requests > 0, msg=f"[{collector_name}] No network requests captured")
        check.is_true(metrics.dom_load_time_ms > 0, msg=f"[{collector_name}] DOM load time is invalid")
        check.is_true(metrics.page_load_time_ms > 0, msg=f"[{collector_name}] Page load time is invalid")
