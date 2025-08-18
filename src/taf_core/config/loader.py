from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .model import (
    ArtifactsConfig,
    BrowserConfig,
    Config,
    ContextConfig,
    TraceConfig,
    VideoConfig,
)


def _load_yaml(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise TypeError(f"Config must be a mapping: {path}")
    return data


def load_config(path: str | None = None) -> Config:
    base = _load_yaml(path)

    browser_src = base.get("browser", {})
    context_src = base.get("context", {})
    artifacts_src = base.get("artifacts", {})

    browser = BrowserConfig(**browser_src)
    context = ContextConfig(**context_src)
    artifacts = ArtifactsConfig(
        video=VideoConfig(**artifacts_src.get("video")),
        screenshots_dir=artifacts_src.get("screenshots_dir"),
        trace=TraceConfig(**artifacts_src.get("trace")),
    )
    parallel_safe = base.get("parallel_safe")

    return Config(browser, context, artifacts, parallel_safe)
