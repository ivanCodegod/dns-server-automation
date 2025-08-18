from playwright.sync_api import Page

from src.taf_core.metrics.browser_metrics import BrowserMetricsCollector
from src.taf_core.metrics.collector import BaseMetricCollector, NetworkMetricsManager


def create_browser_metrics_collector(page: Page) -> BaseMetricCollector:
    return BrowserMetricsCollector(page)


def create_browser_network_metrics_manager(collector: BaseMetricCollector) -> NetworkMetricsManager:
    return NetworkMetricsManager([collector])
