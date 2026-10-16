# Configuration guide

Copy `configs/sample.toml` to a local TOML file when changing settings for an experiment. Keep the sample as a safe, shareable default. Configuration is validated against typed models; unknown keys and invalid parameter ranges fail early.

The `[paths]` section locates local data and artifacts. `[provider]` selects adapters and names an environment variable for the SEC user-agent contact; the secret/contact value itself is never stored in TOML. `[research]` contains the timezone, signal window, warm-up, one-way transaction cost, sector/company caps and sector tilt.

For the pilot, use `configs/pilot.toml`; it pins roster, years, factor/mapping versions, provider settings and local artifact paths. Changing research values changes the research fingerprint. Changing local paths does not. The SEC contact value is only read from the named environment variable and is not written to TOML, fingerprints or manifests. Keep a copy of the exact non-secret config used for a run alongside its manifest.
