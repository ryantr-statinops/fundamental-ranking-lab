# Data lineage and versioning

Every completed data or research run should have a unique UTC run ID and a manifest that names the command, code revision, canonical configuration hash, input artifacts and output artifacts. Content hashes use SHA-256. Existing run outputs are immutable; a rerun receives a new ID rather than replacing prior evidence.

The Stage 00 manifest model and helper implement the initial shape and safe, no-overwrite publication. Later stages must add dependency/tool versions, schema/factor/mapping versions, calendar/cutoff metadata, source retrieval timestamps, and explicit run status/error records. Secrets and personal contact values must not appear in manifests or logs.

Input hashes identify bytes, while research fingerprints identify the declared research parameters. Both are required to establish which data and decisions produced an output. Derived tables should retain input lineage down to source records where feasible.
