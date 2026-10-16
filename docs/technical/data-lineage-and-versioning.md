# Data lineage and versioning

Every completed data or research run should have a unique UTC run ID and a manifest that names the command, code revision, canonical configuration hash, input artifacts and output artifacts. Content hashes use SHA-256. Existing run outputs are immutable; a rerun receives a new ID rather than replacing prior evidence.

The Stage 00 manifest helper implements safe, no-overwrite publication. Manifest v2 adds execution and lockfile hashes, runtime source hash, Python/uv versions, schema/factor/mapping versions, parent run, status/exit code, input/output checksums and canonical table content hashes. Pilot selection records each 16:00 America/New_York cutoff and its UTC equivalent. Raw index entries retain source, URL, retrieval time, filtered response headers and SHA-256; authorization/contact values are excluded.

Input hashes identify bytes, while research fingerprints identify declared research parameters. Both are required to establish which data and decisions produced an output. Derived facts refer to the raw payload hash, accession and XBRL context; ratios carry their supporting fact references. For the pilot, canonical hashes of facts, ratios and coverage exclude volatile run metadata so replay equality can be checked.

`--input-run` checks the parent research hash, roster/evidence hashes, raw-index file hash and every raw payload hash before parsing. Missing or corrupt raw files fail replay and do not trigger provider calls. The manifest’s `code_sha256` fingerprints package source present at execution time; `code_revision` alone may refer to an earlier commit during a local development run.
