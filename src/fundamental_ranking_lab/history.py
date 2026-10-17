"""Immutable historical ingestion, explicit checkpoints and pinned offline inputs."""

from __future__ import annotations

import json
import os
import platform
import tempfile
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from fundamental_ranking_lab.history_config import HistoryConfig, load_history_config
from fundamental_ranking_lab.history_contracts import HistoryBundle
from fundamental_ranking_lab.history_sources import discover
from fundamental_ranking_lab.manifest import (
    RunManifest,
    canonical_sha256,
    new_run_id,
    sha256_file,
    write_manifest,
)
from fundamental_ranking_lab.providers import YFinanceProvider
from fundamental_ranking_lab.raw import RawRecord, RawStore, SecHTTP, SourceError, encode_json


def collect_request(
    request: dict[str, str], http: SecHTTP, store: RawStore, prices: YFinanceProvider
) -> RawRecord:
    if request["kind"] == "prices":
        from fundamental_ranking_lab.pilot_config import RosterEntry

        if not request["url"].startswith("yfinance:"):
            raise ValueError("prices request requires yfinance:symbol")
        symbol = request["url"].split(":", 1)[1]
        entry = RosterEntry(
            entity_id=request["entity_id"],
            cik="0000000000",
            symbol=symbol,
            group="General",
            selection_reason="historical request target only",
            source_url="https://www.sec.gov/",
        )
        return prices.collect(entry, symbol, date.fromisoformat(request["end"]))
    response = http.get(request["url"])
    if request["kind"] in {"submissions", "submissions_history", "filing_index", "companyfacts"}:
        json.loads(response.content)
    return store.put(
        response.content,
        source="sec",
        url=request["url"],
        kind=request["kind"],
        entity_id=request["entity_id"],
        headers=dict(response.headers),
    )


def dump(path: Path, value: object) -> None:
    path.write_bytes(encode_json(value))


def run_path(config: HistoryConfig, run_id: str) -> Path:
    # Reuse the manifest path-component validator before touching a parent run.
    if (
        not run_id
        or any(
            c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
            for c in run_id
        )
        or run_id.startswith(".")
    ):
        raise ValueError("invalid input run id")
    return config.paths.artifact_dir / run_id


def pinned_run(config: HistoryConfig, run_id: str) -> tuple[Path, RunManifest]:
    root = run_path(config, run_id)
    manifest = RunManifest.model_validate_json((root / "manifest.json").read_bytes())
    if manifest.run_id != run_id:
        raise SourceError("parent run identity mismatch")
    for name, digest in manifest.output_artifacts.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or sha256_file(path) != digest:
            raise SourceError("parent artifact checksum mismatch")
    return root, manifest


def validate_bundle(bundle: HistoryBundle, records: list[RawRecord], store: RawStore) -> None:
    hashes = {record.sha256 for record in records}
    for record in records:
        store.read(record)
    if canonical_sha256([m.model_dump() for m in bundle.mapping]) != bundle.mapping_sha256:
        raise SourceError("mapping checksum mismatch")
    referenced = {row.raw_sha256 for row in bundle.evidence}
    referenced.update(row.raw_sha256 for row in bundle.prices)
    if not referenced <= hashes:
        raise SourceError("evidence or price references unpinned raw")
    identities = [(r.evidence_id, r.revision_id) for r in bundle.evidence]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate evidence revision")


def pilot_blockers(config: HistoryConfig) -> list[str]:
    if not config.history.pilot_run:
        return ["pilot_gate_missing"]
    root, manifest = pinned_run(config, config.history.pilot_run)
    if manifest.command != "pilot" or manifest.status != "approved":
        return ["pilot_gate_not_approved"]
    gates = json.loads((root / "group_gates.json").read_bytes())
    passed = {g["group"] for g in gates if g["status"] == "pass"}
    if not config.history.approved_groups or not set(config.history.approved_groups) <= passed:
        return ["pilot_groups_not_approved"]
    return []


def publish(
    config: HistoryConfig,
    temporary: Path,
    run_id: str,
    command: str,
    code: int,
    parent: str | None,
    inputs: dict[str, str],
    content: dict[str, str],
) -> Path:
    from fundamental_ranking_lab.pilot import _command_version, _source_tree_sha256

    dump(temporary / "log.jsonl", {"event": command, "exit_code": code})
    manifest = RunManifest(
        run_id=run_id,
        created_at_utc=datetime.now(UTC),
        command=command,
        config_sha256=config.research_fingerprint(),
        execution_sha256=config.execution_fingerprint(),
        code_revision=_command_version(["git", "rev-parse", "HEAD"]),
        code_sha256=_source_tree_sha256(Path("src/fundamental_ranking_lab")),
        lockfile_sha256=sha256_file(Path("uv.lock")),
        tool_versions={"python": platform.python_version()},
        manifest_version=2,
        parent_run=parent,
        status="recorded" if code == 0 else "failed" if code == 1 else "blocked",
        exit_code=code,
        input_artifacts=inputs,
        content_hashes=content,
        output_artifacts={p.name: sha256_file(p) for p in temporary.iterdir() if p.is_file()},
        schema_versions={"history": "1"},
    )
    write_manifest(manifest, temporary / "manifest.json")
    destination = config.paths.artifact_dir / run_id
    os.rename(temporary, destination)
    return destination


def ingest(
    config_path: Path, input_run: str | None = None, resume_run: str | None = None
) -> tuple[int, Path]:
    if input_run and resume_run:
        raise ValueError("input-run and resume-run are mutually exclusive")
    config = load_history_config(config_path)
    store = RawStore(config.paths.data_dir / "raw")
    records: list[RawRecord] = []
    blockers: list[str] = []
    parent = input_run or resume_run
    checkpoints: dict[str, dict[str, Any]] = {}
    if parent:
        root, manifest = pinned_run(config, parent)
        if manifest.command != "ingest" or manifest.config_sha256 != config.research_fingerprint():
            raise ValueError("parent must be an ingest run with matching history settings")
        bundle = HistoryBundle.model_validate_json((root / "bundle.json").read_bytes())
        records = [
            RawRecord.model_validate(r) for r in json.loads((root / "raw_index.json").read_bytes())
        ]
        checkpoints = json.loads((root / "checkpoints.json").read_bytes())
        validate_bundle(bundle, records, store)
        if input_run:
            blockers = json.loads((root / "blockers.json").read_bytes())
    else:
        bundle = HistoryBundle.model_validate_json(config.history.bundle_path.read_bytes())
        for relative, expected in bundle.raw_files.items():
            path = (config.history.bundle_path.parent / relative).resolve()
            if not path.is_relative_to(config.history.bundle_path.parent.resolve()):
                raise ValueError("bundle raw path escapes bundle directory")
            if sha256_file(path) != expected:
                raise SourceError("bundle raw checksum mismatch")
            records.append(
                store.put(
                    path.read_bytes(),
                    source="fixture" if bundle.prototype else "sec",
                    url=f"local:{relative}",
                    kind="historical_evidence",
                    entity_id="catalog",
                )
            )
        validate_bundle(bundle, records, store)
    config.paths.artifact_dir.mkdir(parents=True, exist_ok=True)
    run_id = new_run_id()
    temporary = Path(tempfile.mkdtemp(prefix=".history-", dir=config.paths.artifact_dir))
    code = 3
    try:
        if not input_run:
            if config.history.mode == "fixture":
                blockers.append("prototype_only")
            else:
                blockers.extend(pilot_blockers(config))
                contact = os.environ.get(config.provider.sec_user_agent_env, "")
                if not contact:
                    blockers.append("sec_contact_not_configured")
                if bundle.prototype:
                    blockers.append("prototype_only")
                if not blockers:
                    http = SecHTTP(contact, config.collection)
                    prices = YFinanceProvider(store, config.collection.requests_per_second)
                    try:
                        for request in bundle.requests:
                            key = canonical_sha256(request)
                            if key in checkpoints:
                                store.read(RawRecord.model_validate(checkpoints[key]))
                                continue
                            record = collect_request(request, http, store, prices)
                            records.append(record)
                            checkpoints[key] = record.model_dump(mode="json")
                            dump(temporary / "checkpoints.json", checkpoints)
                    finally:
                        http.close()
        code = 3 if blockers else 0
    except Exception as exc:
        # Do not serialize provider exception text, which may include contact headers.
        dump(temporary / "failure.json", {"error_type": type(exc).__name__})
        blockers.append("collection_failed")
        code = 1
    dump(temporary / "bundle.json", bundle.model_dump(mode="json"))
    try:
        dump(temporary / "discovery.json", discover(records, store))
    except (ValueError, SourceError):
        blockers.append("historical_discovery_invalid")
        code = 1
        dump(temporary / "discovery.json", [])
    dump(temporary / "raw_index.json", [r.model_dump(mode="json") for r in records])
    dump(temporary / "checkpoints.json", checkpoints)
    dump(temporary / "blockers.json", sorted(set(blockers)))
    destination = publish(
        config,
        temporary,
        run_id,
        "ingest",
        code,
        parent,
        {"config": sha256_file(config_path)},
        {"bundle": canonical_sha256(bundle.model_dump(mode="json"))},
    )
    return code, destination
