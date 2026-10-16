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
| SEC live requests require `FRL_SEC_USER_AGENT` | SEC requests identify the application and a real contact; credentials/contact remain local and outside manifests. The pilot does not invent a placeholder identity. | Contact policy or SEC requirements change. |
| SEC collector is sequential and capped at 2 requests/second | Conservative rate is below SEC’s published ceiling and supports reproducible retry behavior. Timeout is 30 seconds, attempts max at 5; 403 stops collection and 404 is recorded. | Provider policy changes or measured request behavior requires lower limits. |
| Pilot keeps SEC raw immutable and replay offline | Raw payloads are content-addressed and checksum-verified; transformation can be reproduced without hidden network access. | A versioned migration is needed for a new raw format. |
| yfinance price adjustments are explicit but provisional | `auto_adjust=False`, `back_adjust=False`, `actions=True`, `repair=False`; historical split adjustment behavior and event conventions still need verification against evidence. Stooq is not connected. | Overlap audit establishes a validated price source/convention. |
| Roster remains a candidate list until historical proof is checked | Current identifiers and public SEC landing pages do not establish historical listing, SIC, share class or event flags. No return series is used to choose replacements. | A source-by-source review validates each case and cutoff. |

These are technical defaults for the research lab, not evidence that provider coverage, data quality or backtest validity has passed its gates.
