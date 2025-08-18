from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class BrowserConfig:
    name: Literal["chromium", "firefox"] = "chromium"
    headless: bool = True
    channel: str | None = None  # e.g., "chrome", "msedge"
    slow_mo_ms: int = 0
    args: tuple[str, ...] = (
        "--disable-features=AsyncDns",
        "--disable-cache",
        "--disable-application-cache",
        "--ignore-certificate-errors",
    )
    timeout_ms: int = 10000
    dns_server: str | None = None


@dataclass(frozen=True)
class Viewport:
    width: int = 1280
    height: int = 800


@dataclass(frozen=True)
class VideoConfig:
    enabled: bool = True
    mode: Literal["retain-on-failure", "on", "off"] = "retain-on-failure"
    dir: str = "artifacts/video"
    context_level: bool = True  # if True, video recording is per browser context


@dataclass(frozen=True)
class ContextConfig:
    viewport: Viewport = field(default_factory=Viewport)
    permissions: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraceConfig:
    enabled: bool = False
    mode: Literal["retain-on-failure", "on", "off"] = "retain-on-failure"
    dir: str = "artifacts/trace"


@dataclass(frozen=True)
class ArtifactsConfig:
    video: VideoConfig = field(default_factory=VideoConfig)
    screenshots_dir: str = "artifacts/screenshots"
    trace: TraceConfig = field(default_factory=TraceConfig)


@dataclass(frozen=True)
class Config:
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    context: ContextConfig = field(default_factory=ContextConfig)
    artifacts: ArtifactsConfig = field(default_factory=ArtifactsConfig)
    parallel_safe: bool = False  # sync-only, no xdist for now
