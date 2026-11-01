"""Unit tests for quarterly operations, writer lock, and phases."""

from __future__ import annotations

from pathlib import Path

import pytest

from fundamental_ranking_lab.quarterly import LockAcquisitionError, file_lock


def test_file_lock_acquires_and_releases(tmp_path: Path) -> None:
    lock_file = tmp_path / ".operation.lock"
    assert not lock_file.exists()

    with file_lock(lock_file):
        assert lock_file.exists()

    # Automatically unlinked after exiting context
    assert not lock_file.exists()


def test_file_lock_blocks_concurrent_acquisition(tmp_path: Path) -> None:
    lock_file = tmp_path / ".operation.lock"
    with file_lock(lock_file):  # noqa: SIM117
        with pytest.raises(LockAcquisitionError, match="Operation locked"):  # noqa: SIM117
            with file_lock(lock_file):
                pass
    # Once primary lock exits, it can be acquired again
    with file_lock(lock_file):
        assert lock_file.exists()


def test_file_lock_releases_on_exception(tmp_path: Path) -> None:
    lock_file = tmp_path / ".operation.lock"
    with pytest.raises(RuntimeError, match="Simulated crash"), file_lock(lock_file):
        raise RuntimeError("Simulated crash")
    assert not lock_file.exists()


def test_run_quarterly_signal_rejects_future_cutoff(tmp_path: Path) -> None:
    from fundamental_ranking_lab.quarterly import run_quarterly_signal

    cfg = tmp_path / "cfg.toml"
    cfg.write_text("[paths]\n")
    with pytest.raises(ValueError, match="Cannot run signal for future cutoff"):
        run_quarterly_signal("2099-12-31", cfg, output_root=tmp_path)


def test_run_quarterly_reconcile_generates_holdings(tmp_path: Path) -> None:
    from datetime import UTC, datetime
    from decimal import Decimal

    import pyarrow as pa

    from fundamental_ranking_lab.portfolio_contracts import TARGET_WEIGHTS_SCHEMA
    from fundamental_ranking_lab.quarterly import run_quarterly_reconcile
    from fundamental_ranking_lab.storage import write_parquet_atomic

    signal_dir = tmp_path / "signal_run"
    signal_dir.mkdir(parents=True)

    # Create mock target_weights.parquet
    targets = [
        {
            "cutoff": datetime(2025, 12, 31, 21, tzinfo=UTC),
            "entity_id": "aapl",
            "security_id": "AAPL",
            "industry": "Machn",
            "group": "General",
            "raw_score": "0.85",
            "industry_tilt": "1.0",
            "raw_weight": "0.05",
            "target_weight": "0.05",
            "cap_binding": "stock_5pct",
        }
    ]
    write_parquet_atomic(
        pa.Table.from_pylist(targets, schema=TARGET_WEIGHTS_SCHEMA),
        signal_dir / "target_weights.parquet",
        TARGET_WEIGHTS_SCHEMA,
    )

    code, rec_dir = run_quarterly_reconcile(
        parent_signal_dir=signal_dir,
        open_prices={"AAPL": Decimal("180.00")},
        output_root=tmp_path / "reconcile_out",
        starting_nav=Decimal("1000000.00"),
    )
    assert code == 0
    assert (rec_dir / "actual_holdings.parquet").exists()
    assert (rec_dir / "execution_fills.parquet").exists()
    assert (rec_dir / "rebalance_record.parquet").exists()
    assert (rec_dir / "quarterly_phase.parquet").exists()
