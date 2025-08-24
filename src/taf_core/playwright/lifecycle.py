from __future__ import annotations

import logging

from playwright.sync_api import Playwright, sync_playwright


logger = logging.getLogger(__name__)


class PlaywrightLifecycle:
    """Owns Playwright process lifecycle at session scope."""

    def __init__(self) -> None:
        self._pw: Playwright | None = None

    @property
    def pw(self) -> Playwright | None:
        """Getter for the Playwright instance (read-only)."""
        return self._pw

    def start(self) -> Playwright:
        if not self._pw:
            self._pw = sync_playwright().start()
            logger.info("Started Playwright lifecycle")
        return self._pw

    def stop(self) -> None:
        if self._pw:
            self._pw.stop()
            self._pw = None
            logger.info("Stopped Playwright lifecycle")
