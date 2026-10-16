# Local setup

Stage 00 targets Windows and CPython 3.13; CI also validates Ubuntu. Install `uv`, clone the repository, and from its root run:

```powershell
uv python install 3.13
uv sync --locked --extra dev
uv run frl doctor --config configs/sample.toml
```

The `.python-version` and `pyproject.toml` constrain the runtime. `uv.lock` records resolved versions. Keep `.venv`, `.cache`, local datasets and generated artifacts out of commits; `.gitignore` already excludes them. Do not put a SEC contact, token or other secret in the sample config. For real Stage 01 collection, configure the environment variable named in `configs/pilot.toml` as described in [running pipeline](running-pipeline.md). A real contact is required; never use a fabricated address for requests.

For an editable development loop, change package files under `src/`, add offline fixtures under `tests/`, then run the checks listed in the root README. Live Stage 01 collection is separate from the default offline CI suite.
