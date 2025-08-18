from __future__ import annotations

import contextlib

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from playwright.sync_api import Browser, BrowserContext, Page

    from taf_core.config.model import Config


@dataclass
class BrowserSession:
    """Encapsulates Browser + Context + Page creation."""

    config: Config
    browser: Browser

    def new_context(self) -> BrowserContext:
        ctx = self.browser.new_context(
            viewport=self.config.context.viewport,
            bypass_csp=True,
            record_video_dir=(self.config.artifacts.video.dir if self.config.artifacts.video.mode != "off" else None),
        )
        if self.config.context.permissions:
            ctx.grant_permissions(list(self.config.context.permissions))
        return ctx

    def new_page(self, context: BrowserContext | None = None) -> Page:
        ctx = context or self.new_context()
        page = ctx.new_page()
        page.set_default_timeout(self.config.browser.timeout_ms)
        return page

    def close(self) -> None:
        with contextlib.suppress(Exception):
            self.browser.close()
