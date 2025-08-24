from __future__ import annotations

import logging
import time

from typing import TYPE_CHECKING

from playwright.sync_api import Error as PlaywrightError

import allure

from .collector import BaseMetricCollector
from .types import PageLoadMetrics


if TYPE_CHECKING:
    from playwright.sync_api import Page, Request, Response

logger = logging.getLogger(__name__)


class BrowserMetricsCollector(BaseMetricCollector):
    """Collect browser/network metrics for a single page."""

    def __init__(self, page: Page):
        self.page = page
        self._requests: list[Request] = []
        self._responses: list[Response] = []
        self._start_time: float | None = None
        self._end_time: float | None = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def _on_request(self, request: Request):
        self._requests.append(request)

    def _on_response(self, response: Response):
        self._responses.append(response)

    def start(self) -> None:
        self._start_time = time.time()
        self.page.on("request", self._on_request)
        self.page.on("response", self._on_response)

    def stop(self) -> None:
        self._end_time = time.time()

    def _calculate_load_time_ms(self) -> float:
        if self._start_time is not None and self._end_time is not None:
            return (self._end_time - self._start_time) * 1000
        logger.warning("Load time cannot be calculated, start_time or end_time is None")
        return 0.0

    def _calculate_dom_load_time(self) -> float:
        try:
            return self.page.evaluate(
                "() => performance.timing.domContentLoadedEventEnd - performance.timing.navigationStart",
            )
        except PlaywrightError:
            logger.warning("DOM load time cannot be calculated (Playwright error)")
            return 0.0

    def _calculate_page_load_time(self) -> float:
        try:
            return self.page.evaluate(
                "() => performance.timing.loadEventEnd - performance.timing.navigationStart",
            )
        except PlaywrightError:
            logger.warning("Page load time cannot be calculated (Playwright error)")
            return 0.0

    def get_metrics(self) -> PageLoadMetrics:
        metrics = PageLoadMetrics(
            total_requests=len(self._requests),
            dom_load_time_ms=self._calculate_dom_load_time(),
            page_load_time_ms=self._calculate_page_load_time(),
        )
        allure.attach(
            str(metrics),
            name="Browser Metrics",
            attachment_type=allure.attachment_type.TEXT,
        )
        return metrics
