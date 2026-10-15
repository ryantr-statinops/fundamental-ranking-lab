# Local setup

Stage 00 targets Windows and CPython 3.13; CI also validates Ubuntu. Install `uv`, clone the repository, and from its root run:

```powershell
uv python install 3.13
uv sync --locked --extra dev
uv run frl doctor --config configs/sample.toml
```

The `.python-version` and `pyproject.toml` constrain the runtime. `uv.lock` records resolved versions. Keep `.venv`, `.cache`, local datasets and generated artifacts out of commits; `.gitignore` already excludes them. Do not put a SEC contact, token or other secret in the sample config. Set the contact in the environment variable named by the provider config only when a later data command needs it.

For an editable development loop, change package files under `src/`, add offline fixtures under `tests/`, then run the checks listed in the root README. No network-backed data command is part of Stage 00.
