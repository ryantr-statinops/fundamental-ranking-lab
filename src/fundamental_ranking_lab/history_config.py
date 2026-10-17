"""Strict settings for historical collection and offline universe audits."""

from __future__ import annotations

import tomllib
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from fundamental_ranking_lab.config import AppConfig, StrictModel
from fundamental_ranking_lab.manifest import canonical_sha256
from fundamental_ranking_lab.pilot_config import CollectionSettings


class HistorySettings(StrictModel):
    mode: Literal["fixture", "live"] = "fixture"
    bundle_path: Path
    warmup_start: date = date(2007, 1, 1)
    signal_start: date = date(2010, 1, 1)
    signal_end: date = date(2025, 12, 31)
    outcome_end: date = date(2026, 4, 1)
    pilot_run: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
    approved_groups: tuple[str, ...] = ()

    @model_validator(mode="after")
    def chronological(self) -> HistorySettings:
        if not self.warmup_start < self.signal_start <= self.signal_end < self.outcome_end:
            raise ValueError("history dates must be chronological")
        return self


class HistoryConfig(AppConfig):
    history: HistorySettings
    collection: CollectionSettings = Field(default_factory=CollectionSettings)

    def research_fingerprint(self) -> str:
        return canonical_sha256(
            {
                "history": self.history.model_dump(
                    mode="json", exclude={"bundle_path", "pilot_run"}
                ),
                "research": self.research.model_dump(mode="json"),
            }
        )


def load_history_config(path: Path) -> HistoryConfig:
    with path.open("rb") as stream:
        return HistoryConfig.model_validate(tomllib.load(stream))
