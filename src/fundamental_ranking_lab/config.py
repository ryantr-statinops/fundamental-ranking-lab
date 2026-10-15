"""Typed, reproducible application configuration loaded from TOML."""

from __future__ import annotations

import hashlib
import json
import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class PathsConfig(StrictModel):
    data_dir: Path = Path("data")
    artifact_dir: Path = Path("artifacts")


class ProviderConfig(StrictModel):
    sec_user_agent_env: str = "FRL_SEC_USER_AGENT"
    price_provider: str = "yfinance"


class ResearchConfig(StrictModel):
    timezone: str = "America/New_York"
    signal_start: str = "2010-01-01"
    signal_end: str = "2025-12-31"
    warmup_quarters: int = Field(default=12, ge=0, le=80)
    transaction_cost_bps_one_way: float = Field(default=10.0, ge=0, le=500)
    sector_cap: float = Field(default=0.20, gt=0, le=1)
    company_cap: float = Field(default=0.05, gt=0, le=1)
    sector_tilt_lambda: float = Field(default=0.5, ge=0, le=1)

    @model_validator(mode="after")
    def caps_are_feasible_for_a_full_portfolio(self) -> ResearchConfig:
        if self.sector_cap > 1 or self.company_cap > 1:
            raise ValueError("portfolio caps must be at most 100%")
        return self


class AppConfig(StrictModel):
    paths: PathsConfig = Field(default_factory=PathsConfig)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    research: ResearchConfig = Field(default_factory=ResearchConfig)

    def research_fingerprint(self) -> str:
        """Hash only research choices; operational paths do not affect this identity."""
        canonical = json.dumps(
            self.research.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def execution_fingerprint(self) -> str:
        """Hash execution settings without reading or exposing environment secrets."""
        payload = {
            "paths": self.paths.model_dump(mode="json"),
            "provider": self.provider.model_dump(mode="json"),
            "research_fingerprint": self.research_fingerprint(),
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_config(path: Path) -> AppConfig:
    """Read TOML and expand environment variables in configured paths."""
    with path.open("rb") as stream:
        raw: dict[str, Any] = tomllib.load(stream)
    paths = raw.get("paths", {})
    for key, value in paths.items():
        if isinstance(value, str):
            paths[key] = os.path.expandvars(os.path.expanduser(value))
    return AppConfig.model_validate(raw)
