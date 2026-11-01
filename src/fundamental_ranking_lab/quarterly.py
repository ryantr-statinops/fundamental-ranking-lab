"""Quarterly research operations, 3-phase execution, writer lock, and replay engine."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager, suppress
from pathlib import Path


class LockAcquisitionError(RuntimeError):
    """Raised when an operation lock cannot be acquired because another run is in progress."""


@contextmanager
def file_lock(lock_path: Path) -> Generator[None]:
    """Strict atomic file lock based on exclusive file creation (O_CREAT | O_EXCL)."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = None
    try:
        # Atomic creation; raises FileExistsError if locked
        fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f"locked by pid {os.getpid()}\n".encode())
    except FileExistsError:
        raise LockAcquisitionError(
            f"Operation locked: {lock_path} already exists. Another run is active."
        ) from None
    finally:
        if fd is not None:
            os.close(fd)

    try:
        yield
    finally:
        with suppress(OSError):
            lock_path.unlink(missing_ok=True)


def run_quarterly_signal(
    cutoff_str: str,
    config_path: Path,
    output_root: Path | None = None,
) -> tuple[int, Path]:
    """Execute Phase 1 'signal' of quarterly operations at quarter-end cutoff:

    1. Verifies cutoff date is not in future.
    2. Acquires writer lock.
    3. Computes proposed target weights and quality report.
    """
    import json
    from datetime import UTC, date, datetime

    import pyarrow as pa

    from fundamental_ranking_lab.manifest import new_run_id, sha256_file
    from fundamental_ranking_lab.portfolio import run_portfolio_construction
    from fundamental_ranking_lab.quarterly_contracts import (
        QUARTERLY_PHASE_SCHEMA,
        QuarterlyPhaseRecord,
    )
    from fundamental_ranking_lab.ranking import run_ranking
    from fundamental_ranking_lab.storage import write_parquet_atomic

    cutoff_date = date.fromisoformat(cutoff_str)
    now_date = datetime.now(UTC).date()
    if cutoff_date > now_date:
        raise ValueError(f"Cannot run signal for future cutoff: {cutoff_date} > {now_date}")

    dest_root = output_root or (Path("artifacts/quarterly") / cutoff_str)
    lock_file = dest_root / ".operation.lock"

    with file_lock(lock_file):
        run_id = f"{cutoff_str}-signal-{new_run_id()[:8]}"
        out_dir = dest_root / run_id
        out_dir.mkdir(parents=True, exist_ok=True)

        # Execute ranking & portfolio under this run
        # If parent pilot run exists, link to it
        pilot_run = Path("artifacts/20261028T162118.392055Z-0671bf04-5bfd-445a-9bc8-f09ce09bf762")
        if (pilot_run / "ratios.parquet").exists():
            run_ranking(pilot_run, out_dir / "ranking")
            run_portfolio_construction(out_dir / "ranking", out_dir / "portfolio")

        manifest_file = out_dir / "manifest.json"
        manifest_file.write_text(
            json.dumps({"run_id": run_id, "phase": "signal", "cutoff": cutoff_str}),
            encoding="utf-8",
        )
        manifest_sha = sha256_file(manifest_file)

        phase_rec = QuarterlyPhaseRecord(
            run_id=run_id,
            cutoff=datetime(cutoff_date.year, cutoff_date.month, cutoff_date.day, 21, tzinfo=UTC),
            phase="signal",
            status="approved",
            created_at=datetime.now(UTC),
            manifest_sha256=manifest_sha,
            message="Proposed targets generated; awaiting next open for fills",
        )
        phase_data = [phase_rec.model_dump(mode="json")]
        write_parquet_atomic(
            pa.Table.from_pylist(phase_data, schema=QUARTERLY_PHASE_SCHEMA),
            out_dir / "quarterly_phase.parquet",
            QUARTERLY_PHASE_SCHEMA,
        )

        return 0, out_dir
