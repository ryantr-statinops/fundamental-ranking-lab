# Troubleshooting

| Symptom | Check |
|---|---|
| `uv sync --locked` says the lockfile is stale | Run `uv lock`, inspect the dependency diff, then commit `pyproject.toml` and `uv.lock` together according to the repository's per-file delivery workflow. |
| `frl doctor` reports Python 3.13 is required | Run `uv python install 3.13` and execute project commands with `uv run`. |
| Pilot reports `sec_contact_not_configured` | Set a real application/contact string in the local environment variable named by `configs/pilot.toml`, then start a new run. Do not add the email to config or Git. |
| Pilot exits 3 with blocked gates | Read `blockers_final.json`, `coverage.json`, `group_gates.json` and the feasibility report. Exit 3 means the run was recorded but data/review gates remain unresolved. |
| Offline replay reports missing raw/checksum mismatch | Restore the exact raw payload referenced by the parent run or preserve the run as failed. Replay never falls back to the network. |
| SEC returns 403 or retry budget is exhausted | Collection stops or records a sanitized source blocker. Check current SEC policy and contact configuration before starting a new run; do not bypass rate limits. |
| Config validation rejects an unknown field | Check spelling against `configs/sample.toml` and the typed configuration reference. Unknown fields are intentionally not ignored. |
| Parquet publication reports that the target exists | Use a new run/output path. Existing outputs are immutable and are not replaced. |
| Parquet publication fails due to filesystem permissions | Use a writable destination on the same volume as its temporary file; the writer does not copy partial output or overwrite an existing target. |
| CI fails on Windows or Linux only | Reproduce with the same locked environment and inspect path, timezone database and filesystem differences before changing the supported stack. |

`frl doctor` is read-only and offline. It reports environment/config problems; it does not install dependencies or repair files automatically.
