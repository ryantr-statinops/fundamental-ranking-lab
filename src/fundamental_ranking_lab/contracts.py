"""Versioned Arrow contracts and row-level checks for Stage 00 data fixtures."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

import pyarrow as pa

SCHEMA_VERSION = 1
SCHEMA_METADATA = {b"frl.schema_version": str(SCHEMA_VERSION).encode("ascii")}

UTC_TIMESTAMP = pa.timestamp("us", tz="UTC")

IDENTIFIER_HISTORY_SCHEMA = pa.schema(
    [
        pa.field("security_id", pa.string(), nullable=False),
        pa.field("identifier_type", pa.string(), nullable=False),
        pa.field("identifier", pa.string(), nullable=False),
        pa.field("valid_from", pa.date32(), nullable=False),
        pa.field("valid_to", pa.date32()),
        pa.field("known_at", UTC_TIMESTAMP, nullable=False),
        pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        pa.field("source", pa.string(), nullable=False),
        pa.field("source_record_id", pa.string(), nullable=False),
        pa.field("schema_version", pa.int16(), nullable=False),
    ],
    metadata=SCHEMA_METADATA,
)

FACTS_SCHEMA = pa.schema(
    [
        pa.field("entity_id", pa.string(), nullable=False),
        pa.field("concept", pa.string(), nullable=False),
        pa.field("period_start", pa.date32()),
        pa.field("period_end", pa.date32(), nullable=False),
        pa.field("value_text", pa.string()),
        pa.field("unit", pa.string()),
        pa.field("missing_reason", pa.string()),
        pa.field("known_at", UTC_TIMESTAMP, nullable=False),
        pa.field("source", pa.string(), nullable=False),
        pa.field("source_record_id", pa.string(), nullable=False),
        pa.field("schema_version", pa.int16(), nullable=False),
    ],
    metadata=SCHEMA_METADATA,
)

_PROVENANCE_FIELDS = (
    pa.field("source", pa.string(), nullable=False),
    pa.field("source_record_id", pa.string(), nullable=False),
    pa.field("schema_version", pa.int16(), nullable=False),
)


def _versioned_schema(fields: list[pa.Field]) -> pa.Schema:
    return pa.schema([*fields, *_PROVENANCE_FIELDS], metadata=SCHEMA_METADATA)


DOMAIN_SCHEMAS: dict[str, pa.Schema] = {
    "entities": _versioned_schema(
        [
            pa.field("entity_id", pa.string(), nullable=False),
            pa.field("cik", pa.string()),
            pa.field("entity_type", pa.string(), nullable=False),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "securities": _versioned_schema(
        [
            pa.field("security_id", pa.string(), nullable=False),
            pa.field("entity_id", pa.string(), nullable=False),
            pa.field("ticker", pa.string()),
            pa.field("exchange", pa.string(), nullable=False),
            pa.field("security_type", pa.string(), nullable=False),
            pa.field("share_class", pa.string()),
            pa.field("valid_from", pa.date32(), nullable=False),
            pa.field("valid_to", pa.date32()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "memberships": _versioned_schema(
        [
            pa.field("security_id", pa.string(), nullable=False),
            pa.field("universe", pa.string(), nullable=False),
            pa.field("valid_from", pa.date32(), nullable=False),
            pa.field("valid_to", pa.date32()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "industry_history": _versioned_schema(
        [
            pa.field("entity_id", pa.string(), nullable=False),
            pa.field("scheme", pa.string(), nullable=False),
            pa.field("industry_code", pa.string(), nullable=False),
            pa.field("industry_name", pa.string()),
            pa.field("valid_from", pa.date32(), nullable=False),
            pa.field("valid_to", pa.date32()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "filings": _versioned_schema(
        [
            pa.field("accession", pa.string(), nullable=False),
            pa.field("entity_id", pa.string(), nullable=False),
            pa.field("form", pa.string(), nullable=False),
            pa.field("filing_date", pa.date32(), nullable=False),
            pa.field("accepted_at", UTC_TIMESTAMP),
            pa.field("period_end", pa.date32()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "prices": _versioned_schema(
        [
            pa.field("security_id", pa.string(), nullable=False),
            pa.field("timestamp", UTC_TIMESTAMP, nullable=False),
            pa.field("open", pa.float64()),
            pa.field("high", pa.float64()),
            pa.field("low", pa.float64()),
            pa.field("close", pa.float64()),
            pa.field("volume", pa.float64()),
            pa.field("currency", pa.string(), nullable=False),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "corporate_actions": _versioned_schema(
        [
            pa.field("action_id", pa.string(), nullable=False),
            pa.field("security_id", pa.string(), nullable=False),
            pa.field("action_type", pa.string(), nullable=False),
            pa.field("announcement_at", UTC_TIMESTAMP),
            pa.field("effective_date", pa.date32(), nullable=False),
            pa.field("ratio", pa.float64()),
            pa.field("cash_amount", pa.float64()),
            pa.field("currency", pa.string()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
            pa.field("retrieved_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "gate_results": _versioned_schema(
        [
            pa.field("subject_id", pa.string(), nullable=False),
            pa.field("gate_id", pa.string(), nullable=False),
            pa.field("cutoff", UTC_TIMESTAMP, nullable=False),
            pa.field("passed", pa.bool_(), nullable=False),
            pa.field("reason", pa.string()),
            pa.field("details_sha256", pa.string()),
            pa.field("known_at", UTC_TIMESTAMP, nullable=False),
        ]
    ),
    "identifier_history": IDENTIFIER_HISTORY_SCHEMA,
    "facts": FACTS_SCHEMA,
}


def validate_identifier_history(table: pa.Table) -> None:
    """Reject duplicate business keys, bad UTC values and overlapping intervals."""
    validate_table(
        table,
        IDENTIFIER_HISTORY_SCHEMA,
        key_columns=("security_id", "identifier_type", "valid_from", "known_at"),
        interval_columns=("valid_from", "valid_to"),
        interval_group_columns=("security_id", "identifier_type", "known_at"),
    )


def validate_facts(table: pa.Table, *, allowed_units: set[str]) -> None:
    """Validate fact identity, units, as-of timestamps and explicit missing reasons."""
    validate_table(
        table,
        FACTS_SCHEMA,
        key_columns=("entity_id", "concept", "period_end", "known_at", "source_record_id"),
        utc_columns=("known_at",),
        value_reason_columns=("value_text", "missing_reason"),
        allowed_units=allowed_units,
    )


def validate_table(
    table: pa.Table,
    expected_schema: pa.Schema,
    *,
    key_columns: tuple[str, ...] = (),
    interval_columns: tuple[str, str] | None = None,
    interval_group_columns: tuple[str, ...] = (),
    utc_columns: tuple[str, ...] = (),
    value_reason_columns: tuple[str, str] | None = None,
    allowed_units: set[str] | None = None,
) -> None:
    """Validate a table's exact versioned schema and configured row constraints."""
    if not table.schema.equals(expected_schema, check_metadata=True):
        raise ValueError("table schema or schema version does not match the contract")

    rows = table.to_pylist()
    for field in expected_schema:
        if not field.nullable and table[field.name].null_count:
            raise ValueError(f"non-nullable field {field.name!r} contains null values")

    if "schema_version" in table.column_names:
        versions = set(table["schema_version"].to_pylist())
        if versions != {SCHEMA_VERSION}:
            raise ValueError(f"schema_version values must all equal {SCHEMA_VERSION}")

    if key_columns:
        seen: set[tuple[Any, ...]] = set()
        for row in rows:
            key = tuple(row[column] for column in key_columns)
            if any(value is None for value in key):
                raise ValueError(f"business key {key_columns} contains null")
            if key in seen:
                raise ValueError(f"duplicate business key: {key}")
            seen.add(key)

    for column in utc_columns:
        for index, value in enumerate(table[column].to_pylist()):
            if value is not None and (
                not isinstance(value, datetime)
                or value.tzinfo is None
                or value.utcoffset() != timedelta(0)
            ):
                raise ValueError(f"{column}[{index}] must be timezone-aware UTC")

    if interval_columns:
        start_name, end_name = interval_columns
        grouped: dict[tuple[Any, ...], list[tuple[Any, Any]]] = defaultdict(list)
        for row in rows:
            start, end = row[start_name], row[end_name]
            if start is None or (end is not None and end <= start):
                raise ValueError(f"invalid half-open interval in {start_name}/{end_name}")
            group = tuple(row[column] for column in interval_group_columns)
            grouped[group].append((start, end))
        for group, intervals in grouped.items():
            intervals.sort(key=lambda interval: interval[0])
            previous_end: date | datetime | None = None
            has_previous = False
            for start, end in intervals:
                if has_previous and (previous_end is None or start < previous_end):
                    raise ValueError(f"overlapping interval for {group}")
                previous_end = end
                has_previous = True
                if end is None and (start, end) != intervals[-1]:
                    raise ValueError(f"open-ended interval must be last for {group}")

    if value_reason_columns:
        value_name, reason_name = value_reason_columns
        for index, row in enumerate(rows):
            value, reason = row[value_name], row[reason_name]
            if value is None and (not isinstance(reason, str) or not reason.strip()):
                raise ValueError(f"missing {value_name}[{index}] requires a missing_reason")
            if value is not None and reason is not None:
                raise ValueError(f"{value_name}[{index}] has both a value and missing_reason")

    if allowed_units is not None and "unit" in table.column_names:
        unexpected = set(table["unit"].to_pylist()) - allowed_units - {None}
        if unexpected:
            raise ValueError(f"unsupported units: {sorted(unexpected)}")


def canonical_rows_sha256(table: pa.Table, *, sort_by: tuple[str, ...]) -> str:
    """Hash normalized row content independent of row order and Parquet metadata."""
    rows = sorted(table.to_pylist(), key=lambda row: tuple(row[column] for column in sort_by))
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":"), default=_json_default)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"unsupported value in canonical row hash: {type(value).__name__}")
