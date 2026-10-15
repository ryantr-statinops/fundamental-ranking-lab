"""Validated, immutable Parquet publication helpers."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq


def write_parquet_atomic(table: pa.Table, destination: Path, expected_schema: pa.Schema) -> None:
    """Validate schema, write a temporary Parquet file, then publish without overwrite."""
    if not table.schema.equals(expected_schema, check_metadata=True):
        raise ValueError(f"table schema does not match expected schema: {table.schema}")
    for field in expected_schema:
        if not field.nullable and table[field.name].null_count:
            raise ValueError(f"non-nullable field {field.name!r} contains null values")

    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    os.close(fd)
    temporary = Path(temporary_name)
    try:
        pq.write_table(table, temporary)  # type: ignore[no-untyped-call]
        written_schema = pq.read_schema(temporary)  # type: ignore[no-untyped-call]
        if not written_schema.equals(expected_schema, check_metadata=True):
            raise ValueError("Parquet schema changed during serialization")
        with temporary.open("rb+") as stream:
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
