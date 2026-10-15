# Data contracts and storage

Stage 00 establishes storage conventions and a generic Parquet writer; it does not yet implement the domain tables below. Their schemas and constraints are introduced with the data-feasibility pilot and refined before universe-wide ingestion.

## Planned schema family

Schema version 1 is planned for entities/securities, identifier history, memberships, industry history, filings, facts, prices, corporate actions and gate results. Each table will define business keys, nullability, units, source identifiers and versioning before ingestion is enabled.

Identifiers remain strings so CIK leading zeros survive. Calendar dates are separate from timezone-aware UTC timestamps. Effective intervals use `[valid_from, valid_to)`; `known_at` represents when information became public and `retrieved_at` records collection time. Facts retain reported value text, unit, scale and filing context; derived numeric ratios are computed later. Missing values require a reason, and invalid rows are quarantined with an explanation rather than silently dropped.

## Stage 00 Parquet primitive

`write_parquet_atomic` requires an exact Arrow schema, rejects nulls in non-nullable fields, writes and checks a temporary Parquet file beside the target, then publishes without overwriting. It uses an atomic hard link where available and same-volume atomic rename on Windows when hard links are denied. A failed validation leaves no target artifact.

The caller owns table-specific uniqueness, interval, unit and lineage validation until those contracts are implemented in later stages. A successful generic write is not evidence that a domain dataset passed its research gate.
