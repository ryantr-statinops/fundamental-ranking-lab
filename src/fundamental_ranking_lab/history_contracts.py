"""Typed historical evidence; additive contracts leave earlier Arrow schemas intact."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Literal

import pyarrow as pa
from pydantic import Field, field_validator, model_validator

from fundamental_ranking_lab.config import StrictModel


class Evidence(StrictModel):
    evidence_id: str
    revision_id: str
    kind: Literal[
        "security", "identifier", "membership", "industry", "filing", "share", "event", "scope"
    ]
    entity_id: str
    security_id: str | None = None
    source: str
    source_record_id: str
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    known_at: datetime
    valid_from: date
    valid_to: date | None = None
    attributes: dict[str, str] = Field(default_factory=dict)

    @field_validator("known_at")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() != timedelta(0):
            raise ValueError("known_at must be UTC")
        return value

    @model_validator(mode="after")
    def interval(self) -> Evidence:
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("invalid effective interval")
        if (
            self.kind in {"security", "identifier", "membership", "share", "event"}
            and not self.security_id
        ):
            raise ValueError("security evidence requires security_id")
        return self


class Price(StrictModel):
    security_id: str
    session: date
    known_at: datetime
    open: Decimal | None = None
    high: Decimal | None = None
    low: Decimal | None = None
    close: Decimal
    adjusted_close: Decimal | None = None
    volume: Decimal
    currency: str
    convention: str
    raw_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("known_at")
    @classmethod
    def utc(cls, value: datetime) -> datetime:
        return Evidence.utc(value)

    @model_validator(mode="after")
    def finite(self) -> Price:
        values = (self.open, self.high, self.low, self.close, self.adjusted_close, self.volume)
        if any(v is not None and (not v.is_finite() or v < 0) for v in values):
            raise ValueError("price and volume must be finite and nonnegative")
        return self


class MappingRange(StrictModel):
    low: int = Field(ge=0, le=9999)
    high: int = Field(ge=0, le=9999)
    industry: str
    group: str

    @model_validator(mode="after")
    def ordered(self) -> MappingRange:
        if self.high < self.low:
            raise ValueError("invalid SIC range")
        return self


class HistoryBundle(StrictModel):
    prototype: bool = True
    mapping_version: str
    mapping: tuple[MappingRange, ...]
    mapping_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    evidence: tuple[Evidence, ...] = ()
    prices: tuple[Price, ...] = ()
    raw_files: dict[str, str] = Field(default_factory=dict)
    requests: tuple[dict[str, str], ...] = ()
    independent_members: dict[str, tuple[str, ...]] = Field(default_factory=dict)
    completeness_evidence_ids: tuple[str, ...] = ()

    @model_validator(mode="after")
    def mapping_is_unambiguous(self) -> HistoryBundle:
        ordered = sorted(self.mapping, key=lambda r: r.low)
        if any(left.high >= right.low for left, right in zip(ordered, ordered[1:], strict=False)):
            raise ValueError("overlapping SIC mapping ranges")
        for request in self.requests:
            if set(request) != {"url", "kind", "entity_id", "start", "end"}:
                raise ValueError("requests require url/kind/entity_id/start/end")
            if request["kind"] not in {
                "master_index",
                "submissions",
                "submissions_history",
                "filing_text",
                "filing_index",
                "companyfacts",
                "prices",
            }:
                raise ValueError("unsupported historical request kind")
            if date.fromisoformat(request["start"]) > date.fromisoformat(request["end"]):
                raise ValueError("invalid request date range")
        return self


# History contracts are namespaced separately from the original domain schemas.
def history_schema(name: str) -> pa.Schema:
    columns = [
        pa.field(field, pa.string())
        for field in (
            "entity_id",
            "security_id",
            "source",
            "source_record_id",
            "raw_sha256",
            "evidence_id",
            "revision_id",
            "ticker",
            "exchange",
            "share_class",
            "membership",
            "currency",
            "convention",
            "shares",
            "close",
            "adjusted_close",
            "volume",
            "action_type",
        )
    ]
    return pa.schema(
        [
            pa.field("record_id", pa.string(), nullable=False),
            *columns,
            pa.field("known_at", pa.timestamp("us", tz="UTC")),
            pa.field("valid_from", pa.date32()),
            pa.field("valid_to", pa.date32()),
            pa.field("session", pa.date32()),
            pa.field("cutoff", pa.timestamp("us", tz="UTC")),
            pa.field("payload", pa.string(), nullable=False),
            pa.field("schema_version", pa.int16(), nullable=False),
        ],
        metadata={b"frl.schema_version": b"1", b"frl.history_table": name.encode()},
    )


HISTORY_SCHEMAS = {
    name: history_schema(name)
    for name in (
        "entities",
        "securities",
        "identifier_history",
        "memberships",
        "industry_history",
        "filings",
        "shares",
        "prices",
        "corporate_actions",
        "evidence",
        "audit",
        "scope",
    )
}
