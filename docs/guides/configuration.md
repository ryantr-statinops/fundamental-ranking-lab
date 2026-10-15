# Configuration guide

Copy `configs/sample.toml` to a local TOML file when changing settings for an experiment. Keep the sample as a safe, shareable default. Configuration is validated against typed models; unknown keys and invalid parameter ranges fail early.

The `[paths]` section locates local data and artifacts. `[provider]` selects adapters and names an environment variable for the SEC user-agent contact; the secret/contact value itself is never stored in TOML. `[research]` contains the timezone, signal window, warm-up, one-way transaction cost, sector/company caps and sector tilt.

Changing research values changes the research fingerprint. Changing local paths does not. Keep a copy of the exact config used for a run alongside its manifest, after removing any private values.
