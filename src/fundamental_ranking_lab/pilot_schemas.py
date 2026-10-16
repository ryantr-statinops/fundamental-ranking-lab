"""Pilot fact schema v2; Stage 00 schema v1 remains readable and unchanged."""

import pyarrow as pa

FACTS_V2 = pa.schema(
    [
        pa.field("entity_id", pa.string(), nullable=False),
        pa.field("accession", pa.string(), nullable=False),
        pa.field("taxonomy", pa.string(), nullable=False),
        pa.field("tag", pa.string(), nullable=False),
        pa.field("context_id", pa.string(), nullable=False),
        pa.field("period_start", pa.date32()),
        pa.field("period_end", pa.date32(), nullable=False),
        pa.field("unit", pa.string()),
        pa.field("value_text", pa.string(), nullable=False),
        pa.field("normalized_decimal", pa.string()),
        pa.field("scale", pa.int32(), nullable=False),
        pa.field("decimals", pa.string()),
        pa.field("dimensions_json", pa.string(), nullable=False),
        pa.field("filed_date", pa.date32(), nullable=False),
        pa.field("published_at", pa.timestamp("us", tz="UTC")),
        pa.field("publication_precision", pa.string(), nullable=False),
        pa.field("raw_sha256", pa.string(), nullable=False),
        pa.field("form", pa.string(), nullable=False),
        pa.field("document_period_end", pa.date32()),
    ],
    metadata={b"frl.schema_version": b"2", b"frl.table": b"as_filed_facts"},
)

RATIOS_V1 = pa.schema(
    [
        pa.field("entity_id", pa.string(), nullable=False),
        pa.field("cutoff", pa.timestamp("us", tz="UTC"), nullable=False),
        pa.field("ratio", pa.string(), nullable=False),
        pa.field("axis", pa.string(), nullable=False),
        pa.field("value_decimal", pa.string()),
        pa.field("missing_reason", pa.string()),
        pa.field("lineage", pa.list_(pa.field("element", pa.string())), nullable=False),
    ],
    metadata={b"frl.schema_version": b"1", b"frl.table": b"core_ratios"},
)
