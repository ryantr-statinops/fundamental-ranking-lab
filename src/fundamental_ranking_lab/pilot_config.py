"""Validated settings and a frozen, return-blind roster for the pilot."""

from __future__ import annotations

import csv
import tomllib
from collections import Counter
from pathlib import Path
from typing import Literal

from pydantic import Field, model_validator

from fundamental_ranking_lab.config import AppConfig, StrictModel
from fundamental_ranking_lab.manifest import canonical_sha256

GROUP_QUOTAS = {
    "General": 20,
    "Utils": 4,
    "Bank": 4,
    "Insurance": 4,
    "REIT": 4,
    "Other Financials": 4,
}


class CollectionSettings(StrictModel):
    timeout_seconds: float = Field(default=30, gt=0)
    max_attempts: int = Field(default=5, ge=1, le=5)
    requests_per_second: float = Field(default=2, gt=0, le=2)


class PilotSettings(StrictModel):
    roster_path: Path
    evidence_path: Path | None = None
    review_path: Path | None = None
    years: tuple[int, ...] = (2012, 2018, 2022, 2025)
    factor_version: str = "core-v1"
    mapping_version: str = "pilot-v1"


class PilotConfig(AppConfig):
    pilot: PilotSettings
    collection: CollectionSettings = Field(default_factory=CollectionSettings)

    def research_fingerprint(self) -> str:
        return canonical_sha256(
            {
                "research": self.research.model_dump(mode="json"),
                "pilot": self.pilot.model_dump(
                    mode="json", exclude={"roster_path", "evidence_path", "review_path"}
                ),
            }
        )

    def execution_fingerprint(self) -> str:
        return canonical_sha256(
            {
                "research": self.research_fingerprint(),
                "paths": self.paths.model_dump(mode="json"),
                "provider": self.provider.model_dump(mode="json"),
                "collection": self.collection.model_dump(mode="json"),
            }
        )


class RosterEntry(StrictModel):
    entity_id: str = Field(pattern=r"^[a-z0-9-]+$")
    cik: str = Field(pattern=r"^\d{10}$")
    symbol: str
    group: Literal["General", "Utils", "Bank", "Insurance", "REIT", "Other Financials"]
    selection_reason: str
    source_url: str
    evidence_status: Literal["candidate", "verified"] = "candidate"
    loss_case: bool = False
    ticker_change_case: bool = False
    delisting_case: bool = False
    reconcile: bool = False

    @model_validator(mode="after")
    def official_reference(self) -> RosterEntry:
        if not self.source_url.startswith("https://www.sec.gov/"):
            raise ValueError("roster entries require an official SEC source reference")
        return self


def load_pilot_config(path: Path) -> PilotConfig:
    with path.open("rb") as stream:
        return PilotConfig.model_validate(tomllib.load(stream))


def load_roster(path: Path) -> list[RosterEntry]:
    with path.open(encoding="utf-8", newline="") as stream:
        entries = [RosterEntry.model_validate(row) for row in csv.DictReader(stream)]
    if Counter(entry.group for entry in entries) != Counter(GROUP_QUOTAS):
        raise ValueError("roster must contain the locked 20/4/4/4/4/4 group quotas")
    if len({entry.entity_id for entry in entries}) != 40 or len({e.cik for e in entries}) != 40:
        raise ValueError("roster must contain 40 distinct entities and CIKs")
    if sum(e.loss_case for e in entries) < 4:
        raise ValueError("at least four loss cases are required")
    if sum(e.ticker_change_case for e in entries) < 2 or sum(e.delisting_case for e in entries) < 2:
        raise ValueError("at least two ticker/share-class and two merger/delisting cases required")
    selected = [e for e in entries if e.reconcile]
    if len(selected) < 10 or {e.group for e in selected} != set(GROUP_QUOTAS):
        raise ValueError("reconciliation sample must include >=10 entities across all six groups")
    return entries
