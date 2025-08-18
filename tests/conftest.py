import contextlib
import logging

from dataclasses import replace
from pathlib import Path

import pytest

from src.taf_core.config.loader import load_config
from src.taf_core.drivers.browser_factory import BrowserFactory
from src.taf_core.playwright.lifecycle import PlaywrightLifecycle
from src.taf_core.utils.logging_util import configure_logging


logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def _configure_logging():
    """Configure logging once per test session."""
    configure_logging(level=logging.INFO)


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("taf")
    group.addoption("--taf-config", action="store", default="configs/default.yaml", help="Path to YAML config")
    group.addoption("--dns-server", action="store", default=None, help="Override DNS server for resolver rules")


@pytest.fixture(scope="session")
def taf_config(request: pytest.FixtureRequest):
    cfg = load_config(request.config.getoption("--taf-config"))
    dns_server = request.config.getoption("--dns-server")

    if dns_server:
        cfg = replace(cfg, browser=replace(cfg.browser, dns_server=dns_server))

    logger.info(f"Loaded TAF config: {cfg}")
    return cfg


@pytest.fixture(scope="session", autouse=True)
def _ensure_artifacts_dirs(taf_config):
    for p in (
        taf_config.artifacts.screenshots_dir,
        taf_config.artifacts.video.dir,
        taf_config.artifacts.trace.dir,
    ):
        Path(p).mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured artifacts directory exists: {p}")


@pytest.fixture(scope="session")
def playwright_lifecycle():
    lifecycle = PlaywrightLifecycle()
    logger.info("Starting Playwright lifecycle")
    yield lifecycle
    lifecycle.stop()
    logger.info("Stopped Playwright lifecycle")


@pytest.fixture
def browser_session(taf_config, playwright_lifecycle):
    factory = BrowserFactory(lifecycle=playwright_lifecycle, config=taf_config)
    session = factory.create_session()
    logger.info("Created BrowserSession")
    yield session
    session.close()
    logger.info("Closed BrowserSession")


@pytest.fixture
def context(browser_session, taf_config, request):
    ctx = browser_session.new_context()
    # tracing per test
    if taf_config.artifacts.trace.enabled and taf_config.artifacts.trace.mode != "off":
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    logger.info("Created BrowserContext")
    yield ctx
    # stop trace + save on failure or per policy
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    keep = taf_config.artifacts.trace.mode == "on" or (
        failed and taf_config.artifacts.trace.mode == "retain-on-failure"
    )
    if keep:
        logger.info("Stopping tracing and saving trace file")

        out = Path(taf_config.artifacts.trace.dir) / f"{request.node.name}.zip"
        ctx.tracing.stop(path=str(out))
    else:
        ctx.tracing.stop()
    logger.info("Closing BrowserContext")
    ctx.close()


@pytest.fixture
def page(context, taf_config, request):
    pg = context.new_page()
    pg.set_default_timeout(taf_config.browser.timeout_ms)
    logger.info("Created new Page")
    yield pg
    failed = request.node.rep_call.failed if hasattr(request.node, "rep_call") else False
    if failed:
        out = Path(taf_config.artifacts.screenshots_dir) / f"{request.node.name}.png"
        with contextlib.suppress(Exception):
            pg.screenshot(path=str(out), full_page=True)

    logger.info("Closing Page")
    pg.close()
