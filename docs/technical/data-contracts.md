# Data contracts and storage

Stage 00 establishes versioned Arrow schema contracts for domain tables and a generic Parquet writer. Stage 01 adds separate facts schema v2 and ratios schema v1. Pilot-specific identity, mapping and universe-wide validations remain incomplete until historical evidence is audited.

## Planned schema family

`DOMAIN_SCHEMAS` defines schema version 1 for entities, securities, identifier history, memberships, industry history, filings, facts, prices, corporate actions and gate results. Every schema carries source identifiers and a schema version. Identifiers are strings so CIK leading zeros survive. Calendar dates are separate from timezone-aware UTC timestamps. Effective intervals use `[valid_from, valid_to)`; `known_at` represents when information became public and `retrieved_at` records collection time. Facts retain reported value text, unit and period context; derived numeric ratios are computed later. Missing values require a reason, and invalid rows are rejected with an explanation rather than silently dropped.

The Stage 00 validators exercise duplicate business keys, non-overlapping identifier intervals, UTC timestamp schemas, fact units, explicit missing reasons, schema-version metadata and required lineage. Domain-specific checks such as filing amendments, price adjustment semantics and corporate-action reconciliation remain later-stage work.

`facts.parquet` retains normalized decimals as strings alongside original reported text, accession, taxonomy/tag, context, instant/duration, unit, scale/decimals, dimensions, filing-publication precision, source checksum and form. `ratios.parquet` stores one row per entity/cutoff/ratio, a nullable decimal string, missing reason, axis and source lineage. JSON companion artifacts retain membership, market filter, valid-axis counts, issues and group-gate denominators. Schema v1 Stage 00 contracts remain readable; pilot facts use version 2 because their context and precision requirements are more detailed.

## Stage 00 Parquet primitive

`write_parquet_atomic` requires an exact Arrow schema, rejects nulls in non-nullable fields, writes and checks a temporary Parquet file beside the target, then publishes without overwriting. It uses an atomic hard link where available and same-volume atomic rename on Windows when hard links are denied. A failed validation leaves no target artifact.

The caller owns table-specific uniqueness, interval, unit and lineage validation until those contracts are implemented in later stages. A successful generic write is not evidence that a domain dataset passed its research gate.
