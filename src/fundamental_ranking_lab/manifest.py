"""Immutable run-manifest helpers for data and research lineage."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RunManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str
    created_at_utc: datetime
    command: str
    config_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    code_revision: str
    input_artifacts: dict[str, str] = Field(default_factory=dict)
    output_artifacts: dict[str, str] = Field(default_factory=dict)
    manifest_version: int = 1
    execution_sha256: str | None = None
    code_sha256: str | None = None
    lockfile_sha256: str | None = None
    tool_versions: dict[str, str] = Field(default_factory=dict)
    schema_versions: dict[str, str] = Field(default_factory=dict)
    factor_version: str | None = None
    mapping_version: str | None = None
    parent_run: str | None = None
    status: str = "recorded"
    exit_code: int | None = None
    content_hashes: dict[str, str] = Field(default_factory=dict)

    @field_validator("created_at_utc")
    @classmethod
    def require_aware_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at_utc must include a timezone")
        return value.astimezone(UTC)

    @field_validator("run_id")
    @classmethod
    def require_safe_run_id(cls, value: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", value):
            raise ValueError("run_id must be a safe path component")
        return value


def new_run_id(now: datetime | None = None) -> str:
    """Create a sortable UTC identifier with a random suffix."""
    instant = (now or datetime.now(UTC)).astimezone(UTC)
    return f"{instant:%Y%m%dT%H%M%S.%fZ}-{uuid4()}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_manifest(manifest: RunManifest, destination: Path) -> None:
    """Publish a manifest atomically and fail if its destination already exists."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(manifest.model_dump_json(indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, destination)
        except PermissionError:
            if os.name != "nt":
                raise
            # Windows rename is atomic on one volume and refuses an existing target.
            os.rename(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
