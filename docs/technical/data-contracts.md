# Data contracts and storage

Stage 00 establishes versioned Arrow schema contracts for the domain tables and a generic Parquet writer. Pilot-specific business rules, provider mappings and universe-wide validation are still refined in the data-feasibility and audit stages.

## Planned schema family

`DOMAIN_SCHEMAS` defines schema version 1 for entities, securities, identifier history, memberships, industry history, filings, facts, prices, corporate actions and gate results. Every schema carries source identifiers and a schema version. Identifiers are strings so CIK leading zeros survive. Calendar dates are separate from timezone-aware UTC timestamps. Effective intervals use `[valid_from, valid_to)`; `known_at` represents when information became public and `retrieved_at` records collection time. Facts retain reported value text, unit and period context; derived numeric ratios are computed later. Missing values require a reason, and invalid rows are rejected with an explanation rather than silently dropped.

The Stage 00 validators exercise duplicate business keys, non-overlapping identifier intervals, UTC timestamp schemas, fact units, explicit missing reasons, schema-version metadata and required lineage. Domain-specific checks such as filing amendments, price adjustment semantics and corporate-action reconciliation remain later-stage work.

## Stage 00 Parquet primitive

`write_parquet_atomic` requires an exact Arrow schema, rejects nulls in non-nullable fields, writes and checks a temporary Parquet file beside the target, then publishes without overwriting. It uses an atomic hard link where available and same-volume atomic rename on Windows when hard links are denied. A failed validation leaves no target artifact.

The caller owns table-specific uniqueness, interval, unit and lineage validation until those contracts are implemented in later stages. A successful generic write is not evidence that a domain dataset passed its research gate.
