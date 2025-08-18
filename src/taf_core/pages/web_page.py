from __future__ import annotations

from .base_page import BasePage


class WebPage(BasePage):
    def open(self) -> WebPage:
        self.goto("/")
        return self
