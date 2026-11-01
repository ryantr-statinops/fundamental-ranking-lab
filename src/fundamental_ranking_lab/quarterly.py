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
