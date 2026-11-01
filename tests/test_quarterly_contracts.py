"""Unit tests for quarterly operational contracts and schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pyarrow as pa
import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.quarterly_contracts import (
    EXECUTION_FILL_SCHEMA,
    QUARTERLY_PHASE_SCHEMA,
    BackupManifest,
    ExecutionFillRecord,
    QuarterlyPhaseRecord,
)


def test_quarterly_phase_contract() -> None:
    rec = QuarterlyPhaseRecord(
        run_id="20251231-signal-01",
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        phase="signal",
        status="approved",
        created_at=datetime(2025, 12, 31, 21, 5, tzinfo=UTC),
        manifest_sha256="a" * 64,
        message="Signal generation complete",
    )
    assert rec.phase == "signal"
    assert rec.status == "approved"
    assert pa.types.is_string(QUARTERLY_PHASE_SCHEMA.field("phase").type)

    with pytest.raises(ValidationError):
        QuarterlyPhaseRecord(
            run_id="test",
            cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
            phase="invalid_phase",  # type: ignore[arg-type]
            created_at=datetime(2025, 12, 31, 21, 5, tzinfo=UTC),
            manifest_sha256="a" * 64,
        )


def test_execution_fill_contract() -> None:
    fill = ExecutionFillRecord(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        security_id="AAPL",
        side="buy",
        target_weight=Decimal("0.05"),
        open_price=Decimal("180.50"),
        shares_filled=Decimal("277.0"),
        notional_filled=Decimal("49998.50"),
        fee_incurred=Decimal("49.9985"),
    )
    assert fill.side == "buy"
    assert fill.shares_filled == Decimal("277.0")
    assert pa.types.is_string(EXECUTION_FILL_SCHEMA.field("open_price").type)


def test_backup_manifest_contract() -> None:
    bm = BackupManifest(
        backup_id="backup-20251231",
        run_id="run-20251231",
        backed_up_at=datetime(2025, 12, 31, 22, tzinfo=UTC),
        file_count=15,
        total_bytes=1048576,
        checksums={"manifest.json": "0" * 64},
    )
    assert bm.file_count == 15
    assert len(bm.checksums) == 1
