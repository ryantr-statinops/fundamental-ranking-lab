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
