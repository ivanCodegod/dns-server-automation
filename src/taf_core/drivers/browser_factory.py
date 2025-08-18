from __future__ import annotations

import os

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .session import BrowserSession


if TYPE_CHECKING:
    from taf_core.config.model import Config
    from taf_core.playwright.lifecycle import PlaywrightLifecycle


@dataclass
class BrowserFactory:
    """Creates BrowserSession configured from Config."""

    lifecycle: PlaywrightLifecycle
    config: Config

    def _build_launch_kwargs(self) -> dict:
        args: list[str] = list(self.config.browser.args)

        # DNS override: ENV takes precedence over config.browser.dns_server; Can happen if
        # executed from Docker Container
        dns_server = os.getenv("DNS_SERVER") or self.config.browser.dns_server
        if dns_server:
            args.append(f"--host-resolver-rules=MAP * {dns_server}")

        kwargs: dict = {
            "headless": self.config.browser.headless,
            "slow_mo": self.config.browser.slow_mo_ms,
            "args": args,
        }

        if self.config.browser.channel:
            kwargs["channel"] = self.config.browser.channel

        return kwargs

    def create_session(self) -> BrowserSession:
        pw = self.lifecycle.start()
        launch_kwargs = self._build_launch_kwargs()

        if self.config.browser.name == "chromium":
            browser = pw.chromium.launch(**launch_kwargs)
        else:
            browser = pw.webkit.launch(**launch_kwargs)

        return BrowserSession(config=self.config, browser=browser)
