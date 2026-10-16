# Stage 00 architecture

This page records the Stage 00 foundation and the Stage 01 pilot implementation. The pilot can parse pinned original filings, compute pilot ratios and emit blocked feasibility artifacts. Historical identity/membership, universe completeness and real-source coverage have not passed their data gates.

## Runtime boundaries

- `src/fundamental_ranking_lab/` is the installable Python package; `frl` and `python -m fundamental_ranking_lab` are its supported entry points.
- TOML configuration is parsed and validated at the edge. Research logic should receive typed values and must not read environment variables directly.
- Provider integrations belong behind adapters. `doctor` is local and read-only. Stage 01 exposes an SEC collector and yfinance price adapter; live collection requires a local SEC contact and verified evidence before price requests.
- Parquet is the intended durable tabular format. DuckDB is an embedded query engine and any derived catalog remains rebuildable.
- `data/`, `artifacts/`, virtual environments and caches are local runtime state, excluded from Git.

## Current package boundaries

Stage 00 implements typed configuration, `doctor`, manifest/hash helpers and schema-checked Parquet publication. Stage 01 adds `pilot_config`, `raw`, `providers`, `filings`, `features`, `pilot_schemas`, `gates`, `review` and `pilot`, exposed through `frl pilot`. Ranking, backtest and performance reporting remain unimplemented.

## Reproducibility

`uv.lock` fixes resolved dependencies. Manifest v2 records command, UTC creation time, research/execution hashes, Git revision, runtime source hash, lockfile hash, Python/uv versions, schema/factor/mapping versions, input/output file hashes and canonical content hashes. The research fingerprint excludes machine-specific paths and provider contact details. The SEC contact value is not serialized.

Raw payloads are content-addressed below `data/raw`; run outputs live below `artifacts/<run_id>`. The CLI creates a new run directory and never overwrites it. `--input-run` verifies the parent manifest, raw index and each payload before transforming; a missing cache entry fails without downloading.

## Platform support

The local development target is Windows with CPython 3.13. CI also runs the same locked offline test suite on Ubuntu. A stage is not considered portable until both matrix jobs pass.
