"""Read-only checks for the local Stage 00 runtime."""

from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

from fundamental_ranking_lab.config import AppConfig, load_config

REQUIRED_DISTRIBUTIONS = (
    "duckdb",
    "exchange-calendars",
    "httpx",
    "numpy",
    "pandas",
    "pyarrow",
    "pydantic",
    "typer",
    "yfinance",
)


def diagnostics(config_path: Path | None = None) -> tuple[bool, list[str], AppConfig | None]:
    """Return environment checks without creating files or using the network."""
    checks: list[str] = []
    ok = True
    if sys.version_info[:2] != (3, 13):
        ok = False
        checks.append(
            f"FAIL Python: expected 3.13, found {sys.version_info.major}.{sys.version_info.minor}"
        )
    else:
        checks.append(
            f"OK Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        )

    for distribution in REQUIRED_DISTRIBUTIONS:
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            ok = False
            checks.append(f"FAIL dependency: {distribution} is not installed")
        else:
            checks.append(f"OK dependency: {distribution} {version}")

    config: AppConfig | None = None
    if config_path is not None:
        try:
            config = load_config(config_path)
        except Exception as exc:
            ok = False
            checks.append(f"FAIL config: {config_path}: {exc}")
        else:
            checks.append(f"OK config: {config_path}")
            checks.append(f"OK research fingerprint: {config.research_fingerprint()}")
    return ok, checks, config
