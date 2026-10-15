# Configuration and CLI

Install the package from the repository root and validate the example config:

```powershell
uv sync --locked --extra dev
uv run frl doctor --config configs/sample.toml
```

The TOML sample contains no credentials. It separates local paths, provider selection and research parameters. Unknown keys are rejected so a misspelling cannot silently select a default. Path values support `~` and environment-variable expansion. The SEC user-agent contact is supplied at runtime through the environment variable named by `provider.sec_user_agent_env`; its value is never written into a fingerprint or manifest.

`frl doctor` checks that CPython 3.13 and the required runtime distributions are available, and can validate a supplied config. It does not create directories, install packages or access the network. A configuration error or incompatible runtime returns a nonzero exit code.

The research fingerprint captures research choices without local paths. The execution fingerprint also includes paths and provider settings. A manifest must additionally capture code revision and hashes of actual inputs and outputs; a config hash alone does not identify data contents.
