"""Data contracts and schemas for quarterly operations, execution phases, and replay."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

import pyarrow as pa

from fundamental_ranking_lab.config import StrictModel


class QuarterlyPhaseRecord(StrictModel):
    run_id: str
    cutoff: datetime
    phase: Literal["signal", "reconcile", "outcome"]
    status: Literal["approved", "blocked", "failed"] = "approved"
    created_at: datetime
    parent_run_id: str | None = None
    manifest_sha256: str
    message: str | None = None


class ExecutionFillRecord(StrictModel):
    cutoff: datetime
    security_id: str
    side: Literal["buy", "sell", "hold"]
    target_weight: Decimal
    open_price: Decimal
    shares_filled: Decimal
    notional_filled: Decimal
    fee_incurred: Decimal


class BackupManifest(StrictModel):
    backup_id: str
    run_id: str
    backed_up_at: datetime
    file_count: int
    total_bytes: int
    checksums: dict[str, str]


QUARTERLY_PHASE_SCHEMA = pa.schema(
    [
        ("run_id", pa.string()),
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("phase", pa.string()),
        ("status", pa.string()),
        ("created_at", pa.timestamp("us", tz="UTC")),
        ("parent_run_id", pa.string()),
        ("manifest_sha256", pa.string()),
        ("message", pa.string()),
    ]
)

EXECUTION_FILL_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("security_id", pa.string()),
        ("side", pa.string()),
        ("target_weight", pa.string()),
        ("open_price", pa.string()),
        ("shares_filled", pa.string()),
        ("notional_filled", pa.string()),
        ("fee_incurred", pa.string()),
    ]
)
