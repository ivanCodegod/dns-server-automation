from __future__ import annotations

from playwright.sync_api import Playwright, sync_playwright


class PlaywrightLifecycle:
    """Owns Playwright process lifecycle at session scope."""

    def __init__(self) -> None:
        self._pw: Playwright | None = None

    def start(self) -> Playwright:
        if not self._pw:
            self._pw = sync_playwright().start()
        return self._pw

    def stop(self) -> None:
        if self._pw:
            self._pw.stop()
            self._pw = None
