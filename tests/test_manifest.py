from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.manifest import RunManifest, new_run_id, sha256_file, write_manifest


def manifest() -> RunManifest:
    return RunManifest(
        run_id=new_run_id(),
        created_at_utc=datetime(2026, 1, 2, tzinfo=UTC),
        command="doctor",
        config_sha256="a" * 64,
        code_revision="abc123",
    )


def test_manifest_requires_aware_time_and_safe_run_id() -> None:
    with pytest.raises(ValidationError):
        RunManifest(
            run_id="../escape",
            created_at_utc=datetime(2026, 1, 2),
            command="doctor",
            config_sha256="a" * 64,
            code_revision="abc123",
        )


def test_run_id_uses_utc_timestamp_and_uuid() -> None:
    run_id = new_run_id(datetime(2026, 1, 2, tzinfo=UTC))
    timestamp, identifier = run_id.split("-")[:1][0], "-".join(run_id.split("-")[1:])
    assert timestamp.startswith("20260102T000000.") and timestamp.endswith("Z")
    UUID(identifier)


def test_manifest_publish_is_atomic_and_does_not_overwrite(tmp_path: Path) -> None:
    destination = tmp_path / "manifest.json"
    write_manifest(manifest(), destination)
    assert '"run_id"' in destination.read_text(encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_manifest(manifest(), destination)


def test_sha256_file(tmp_path: Path) -> None:
    source = tmp_path / "input.bin"
    source.write_bytes(b"fixture")
    assert sha256_file(source) == "f16d05ec6b29248d2c61adb1e9263f78e4f7bace1b955014a2d17872cfe4064d"
