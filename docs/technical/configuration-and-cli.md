# Configuration and CLI

Install the package from the repository root and validate the sample config:

```powershell
uv sync --locked --extra dev
uv run frl doctor --config configs/sample.toml
```

The TOML sample contains no credentials. It separates local paths, provider selection and research parameters. Unknown keys are rejected so a misspelling cannot silently select a default. Path values support `~` and environment-variable expansion. The SEC user-agent contact is supplied at runtime through the environment variable named by `provider.sec_user_agent_env`; its value is never written into a fingerprint or manifest.

`frl doctor` checks that CPython 3.13 and the required runtime distributions are available, and can validate a supplied config. It does not create directories, install packages or access the network. A configuration error or incompatible runtime returns a nonzero exit code.

The research fingerprint captures research choices without local paths. The execution fingerprint also includes paths and provider settings. A manifest must additionally capture code revision and hashes of actual inputs and outputs; a config hash alone does not identify data contents.

## Stage 01 pilot

`configs/pilot.toml` selects the 40-row CSV roster, cutoff years, SEC contact environment-variable name, yfinance provider, data/artifact roots, collection timeout/retry/rate limits and factor/mapping versions. Unknown keys fail validation. Roster flags are candidates requiring historical-source verification, not confirmed membership or event evidence.

```text
uv run frl pilot --config configs/pilot.toml
uv run frl pilot --config configs/pilot.toml --input-run <run_id>
```

The first form collects SEC filings and, after identity/share-class evidence, daily prices. The second is offline and reads only raw files pinned by the named parent run. Results include selection, raw index, coverage, facts/ratios Parquet, reconciliation CSV, group gates, blockers, manifest and feasibility Markdown/HTML. Exit codes are 0 for all required gates passed, 2 for invalid configuration, 3 for a blocked/pending data gate and 1 for an execution failure. A blocked code 3 can still contain useful audit artifacts.

The manifest’s source hash fingerprints the actual package files even while the checkout has uncommitted changes. Its Git revision identifies the current HEAD, so both fields are required when runs occur during development.
