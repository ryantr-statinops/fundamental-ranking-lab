from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fundamental_ranking_lab.storage import write_parquet_atomic


def test_parquet_round_trip_and_no_overwrite(tmp_path: Path) -> None:
    schema = pa.schema(
        [pa.field("security_id", pa.string(), nullable=False), pa.field("value", pa.float64())]
    )
    table = pa.Table.from_pylist([{"security_id": "0000123456", "value": 1.25}], schema=schema)
    destination = tmp_path / "part.parquet"
    write_parquet_atomic(table, destination, schema)
    assert pq.read_table(destination).to_pylist() == [{"security_id": "0000123456", "value": 1.25}]
    with pytest.raises(FileExistsError):
        write_parquet_atomic(table, destination, schema)


def test_parquet_rejects_schema_mismatch(tmp_path: Path) -> None:
    expected = pa.schema([pa.field("value", pa.int64())])
    actual = pa.table({"value": [1.0]})
    destination = tmp_path / "invalid.parquet"
    with pytest.raises(ValueError, match="schema"):
        write_parquet_atomic(actual, destination, expected)
    assert not destination.exists()


def test_parquet_rejects_null_in_nonnullable_field(tmp_path: Path) -> None:
    schema = pa.schema([pa.field("security_id", pa.string(), nullable=False)])
    table = pa.Table.from_pylist([{"security_id": None}], schema=schema)
    with pytest.raises(ValueError, match="null"):
        write_parquet_atomic(table, tmp_path / "invalid.parquet", schema)
