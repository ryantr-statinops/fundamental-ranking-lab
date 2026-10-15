# Troubleshooting

| Symptom | Check |
|---|---|
| `uv sync --locked` says the lockfile is stale | Run `uv lock`, inspect the dependency diff, then commit `pyproject.toml` and `uv.lock` together according to the repository's per-file delivery workflow. |
| `frl doctor` reports Python 3.13 is required | Run `uv python install 3.13` and execute project commands with `uv run`. |
| Config validation rejects an unknown field | Check spelling against `configs/sample.toml` and the typed configuration reference. Unknown fields are intentionally not ignored. |
| Parquet publication reports that the target exists | Use a new run/output path. Existing outputs are immutable and are not replaced. |
| Parquet publication fails due to filesystem permissions | Use a writable destination on the same volume as its temporary file; the writer does not copy partial output or overwrite an existing target. |
| CI fails on Windows or Linux only | Reproduce with the same locked environment and inspect path, timezone database and filesystem differences before changing the supported stack. |

`frl doctor` is read-only and offline. It reports environment/config problems; it does not install dependencies or repair files automatically.
