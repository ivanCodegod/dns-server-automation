import contextlib
import logging

from dataclasses import replace
from pathlib import Path

import pytest

from src.taf_core.config.loader import load_config
from src.taf_core.drivers.browser_factory import BrowserSessionFactory
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

    if dns_server:  # override DNS server if provided from CLI
        cfg = replace(cfg, browser=replace(cfg.browser, dns_server=dns_server))

    logger.info(f"Loaded TAF config: {cfg}")  # TODO: Use pprint.pformat(cfg) for better formatting
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
    lifecycle.start()
    yield lifecycle
    lifecycle.stop()


@pytest.fixture
def browser_session(taf_config, playwright_lifecycle):
    factory = BrowserSessionFactory(config=taf_config)
    session = factory.create_session(pw=playwright_lifecycle.pw)
    yield session
    session.close_browser()


@pytest.fixture
def context(browser_session, taf_config, request):
    ctx = browser_session.new_context()
    # tracing per test
    if taf_config.artifacts.trace.enabled and taf_config.artifacts.trace.mode != "off":
        ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    logger.info("Created Browser Context")
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
    logger.info("Closing Browser Context")
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
