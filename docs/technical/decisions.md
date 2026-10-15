# Technical decisions — Stage 00

| Decision | Rationale | Revisit when |
|---|---|---|
| CPython 3.13 only for v1 | One minor runtime reduces environment variation; local and CI are pinned alike. | A required dependency lacks a compatible wheel or measured need justifies another runtime. |
| `uv` with committed lockfile | Reproducible resolution and a compact local workflow. | Tooling constraints prevent locked install on supported platforms. |
| `src/` package with Hatchling | Keeps imports tied to the installed package and supports a standard build backend. | Packaging needs change. |
| pandas/NumPy, Arrow/Parquet and DuckDB | Covers tabular transformation, numerical work, durable files and local SQL. | A measured scale or compatibility issue demonstrates a better fit. |
| Pydantic v2, TOML and Typer | Typed config validation and a small CLI boundary. | Config or command surface materially outgrows these interfaces. |
| Local data and artifact directories are ignored | Research inputs and generated results are not source code and may contain large or restricted files. | A reviewed, sanitized fixture is intentionally committed. |
| Parquet publication does not overwrite | Preserves run evidence and prevents partial replacement. | Only with a versioned migration strategy that preserves prior artifacts. |
| CI runs offline tests on Windows and Linux | Covers the local target and reproducibility platform without provider dependence. | Additional supported platforms are adopted. |

These are technical defaults for the research lab, not evidence that provider coverage, data quality or backtest validity has passed its gates.
