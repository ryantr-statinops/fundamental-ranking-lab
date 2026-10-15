from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fundamental_ranking_lab.contracts import (
    DOMAIN_SCHEMAS,
    FACTS_SCHEMA,
    IDENTIFIER_HISTORY_SCHEMA,
    canonical_rows_sha256,
    validate_facts,
    validate_identifier_history,
)
from fundamental_ranking_lab.storage import write_parquet_atomic


def identifier(
    start: date, end: date | None, *, known_at: datetime | None = None, ticker: str = "EXAMPLE"
) -> dict[str, object]:
    return {
        "security_id": "sec-1",
        "identifier_type": "ticker",
        "identifier": ticker,
        "valid_from": start,
        "valid_to": end,
        "known_at": known_at or datetime(2025, 1, 1, tzinfo=UTC),
        "retrieved_at": datetime(2025, 1, 2, tzinfo=UTC),
        "source": "fixture",
        "source_record_id": f"record-{start.isoformat()}",
        "schema_version": 1,
    }


def fact(**overrides: object) -> dict[str, object]:
    row: dict[str, object] = {
        "entity_id": "entity-1",
        "concept": "Revenue",
        "period_start": date(2024, 1, 1),
        "period_end": date(2024, 12, 31),
        "value_text": "123.45",
        "unit": "USD",
        "missing_reason": None,
        "known_at": datetime(2025, 2, 1, tzinfo=UTC),
        "source": "fixture",
        "source_record_id": "accession-1",
        "schema_version": 1,
    }
    row.update(overrides)
    return row


def test_identifier_contract_rejects_duplicate_business_key() -> None:
    rows = [identifier(date(2020, 1, 1), date(2021, 1, 1))] * 2
    with pytest.raises(ValueError, match="duplicate business key"):
        validate_identifier_history(pa.Table.from_pylist(rows, schema=IDENTIFIER_HISTORY_SCHEMA))


def test_schema_registry_has_versioned_contract_for_each_stage_00_table() -> None:
    assert set(DOMAIN_SCHEMAS) == {
        "entities",
        "securities",
        "identifier_history",
        "memberships",
        "industry_history",
        "filings",
        "facts",
        "prices",
        "corporate_actions",
        "gate_results",
    }
    assert all(
        schema.metadata == {b"frl.schema_version": b"1"} for schema in DOMAIN_SCHEMAS.values()
    )


def test_identifier_contract_rejects_overlapping_intervals() -> None:
    rows = [
        identifier(date(2020, 1, 1), date(2021, 7, 1), ticker="OLD"),
        identifier(date(2021, 1, 1), None, ticker="NEW"),
    ]
    with pytest.raises(ValueError, match="overlapping interval"):
        validate_identifier_history(pa.Table.from_pylist(rows, schema=IDENTIFIER_HISTORY_SCHEMA))


def test_identifier_contract_accepts_adjacent_half_open_intervals() -> None:
    rows = [
        identifier(date(2020, 1, 1), date(2021, 1, 1), ticker="OLD"),
        identifier(date(2021, 1, 1), None, ticker="NEW"),
    ]
    validate_identifier_history(pa.Table.from_pylist(rows, schema=IDENTIFIER_HISTORY_SCHEMA))


def test_identifier_contract_rejects_naive_timestamp_schema() -> None:
    naive_schema = IDENTIFIER_HISTORY_SCHEMA.set(
        IDENTIFIER_HISTORY_SCHEMA.get_field_index("known_at"),
        pa.field("known_at", pa.timestamp("us"), nullable=False),
    )
    table = pa.Table.from_pylist([identifier(date(2020, 1, 1), None)], schema=naive_schema)
    with pytest.raises(ValueError, match="schema or schema version"):
        validate_identifier_history(table)


def test_fact_missing_value_requires_reason() -> None:
    table = pa.Table.from_pylist([fact(value_text=None)], schema=FACTS_SCHEMA)
    with pytest.raises(ValueError, match="requires a missing_reason"):
        validate_facts(table, allowed_units={"USD", "shares"})


def test_fact_rejects_unknown_unit_and_incomplete_lineage() -> None:
    bad_unit = pa.Table.from_pylist([fact(unit="bananas")], schema=FACTS_SCHEMA)
    with pytest.raises(ValueError, match="unsupported units"):
        validate_facts(bad_unit, allowed_units={"USD", "shares"})

    missing_source = pa.Table.from_pylist([fact(source_record_id=None)], schema=FACTS_SCHEMA)
    with pytest.raises(ValueError, match="non-nullable field 'source_record_id'"):
        validate_facts(missing_source, allowed_units={"USD", "shares"})


def test_canonical_hash_is_order_independent_and_parquet_round_trips(tmp_path: Path) -> None:
    rows = [fact(source_record_id="b"), fact(source_record_id="a")]
    table = pa.Table.from_pylist(rows, schema=FACTS_SCHEMA)
    validate_facts(table, allowed_units={"USD", "shares"})
    reordered = pa.Table.from_pylist(list(reversed(rows)), schema=FACTS_SCHEMA)
    assert canonical_rows_sha256(table, sort_by=("source_record_id",)) == canonical_rows_sha256(
        reordered, sort_by=("source_record_id",)
    )

    destination = tmp_path / "facts.parquet"
    write_parquet_atomic(table, destination, FACTS_SCHEMA)
    stored = pq.read_table(destination)
    validate_facts(stored, allowed_units={"USD", "shares"})
    assert canonical_rows_sha256(table, sort_by=("source_record_id",)) == canonical_rows_sha256(
        stored, sort_by=("source_record_id",)
    )
