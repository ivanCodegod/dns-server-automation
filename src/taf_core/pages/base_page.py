from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from playwright.sync_api import Page


class BasePage:
    """Common page utilities and conventions."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    def goto(self, path: str = "/") -> None:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        self.page.goto(url, wait_until="load")  # wait for full load
