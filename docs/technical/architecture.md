# Stage 00 architecture

This page records the small executable foundation delivered by Stage 00. It does not claim that the research pipeline, point-in-time universe, or provider ingestion is implemented.

## Runtime boundaries

- `src/fundamental_ranking_lab/` is the installable Python package; `frl` and `python -m fundamental_ranking_lab` are its supported entry points.
- TOML configuration is parsed and validated at the edge. Research logic should receive typed values and must not read environment variables directly.
- Provider integrations belong behind adapters. The Stage 00 `doctor` command is local and read-only; it makes no provider requests.
- Parquet is the intended durable tabular format. DuckDB is an embedded query engine and any derived catalog remains rebuildable.
- `data/`, `artifacts/`, virtual environments and caches are local runtime state, excluded from Git.

## Current package boundaries

Stage 00 implements typed configuration, a read-only doctor command, manifest/hash helpers and a schema-checked Parquet publication primitive. Universe, feature, ranking, backtest and reporting modules are introduced only by their corresponding stages. The package should not expose unimplemented commands as successful operations.

## Reproducibility

`uv.lock` fixes resolved dependencies. A run manifest records the command, UTC creation time, config hash, code revision and input/output content hashes. The research fingerprint excludes machine-specific paths and provider contact details. Execution identity can include operational settings but never reads the secret value named by the SEC user-agent environment key.

## Platform support

The local development target is Windows with CPython 3.13. CI also runs the same locked offline test suite on Ubuntu. A stage is not considered portable until both matrix jobs pass.
