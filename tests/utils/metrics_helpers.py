from src.taf_core.metrics.collector import BaseMetricCollector
from src.taf_core.pages.base_page import BasePage


def collect_metrics_for_page(browser_collector: BaseMetricCollector, web_page: BasePage):
    with browser_collector:
        web_page.open()
