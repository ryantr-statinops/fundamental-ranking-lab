"""Offline historical-universe audit; prototype inputs cannot certify a scope."""

from __future__ import annotations

import json
import tempfile
from collections import Counter
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import exchange_calendars as xcals  # type: ignore[import-untyped]
import pyarrow as pa

from fundamental_ranking_lab.history import (
    dump,
    pilot_blockers,
    pinned_run,
    publish,
    validate_bundle,
)
from fundamental_ranking_lab.history_config import load_history_config
from fundamental_ranking_lab.history_contracts import HISTORY_SCHEMAS, HistoryBundle
from fundamental_ranking_lab.history_market import market_filters, normalize_events
from fundamental_ranking_lab.manifest import canonical_sha256, new_run_id, sha256_file
from fundamental_ranking_lab.raw import RawRecord, RawStore
from fundamental_ranking_lab.storage import write_parquet_atomic
from fundamental_ranking_lab.universe import asof, resolve_universe


def quarter_cutoffs(start: date, end: date) -> list[datetime]:
    calendar = xcals.get_calendar("XNYS", start=f"{start.year}-01-01", end=f"{end.year}-12-31")
    cutoffs = []
    for year in range(start.year, end.year + 1):
        for month in (3, 6, 9, 12):
            last = 31 if month in (3, 12) else 30
            sessions = calendar.sessions_in_range(
                f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last}"
            )
            day = sessions[-1].date()
            if start <= day <= end:
                cutoffs.append(
                    datetime(
                        day.year, day.month, day.day, 16, tzinfo=ZoneInfo("America/New_York")
                    ).astimezone(UTC)
                )
    return cutoffs


def write_table(root: Path, name: str, rows: list[dict[str, Any]]) -> str:
    schema = HISTORY_SCHEMAS[name]
    payloads = sorted(
        json.dumps(r, sort_keys=True, default=str, separators=(",", ":")) for r in rows
    )
    table = pa.Table.from_pylist(
        [_arrow_row(p, schema) for p in payloads],
        schema=schema,
    )
    write_parquet_atomic(table, root / f"{name}.parquet", schema)
    return canonical_sha256(payloads)


def _arrow_row(payload: str, schema: pa.Schema) -> dict[str, Any]:
    row = json.loads(payload)
    flat = {**row.get("attributes", {}), **row}
    result = {field.name: flat.get(field.name) for field in schema}
    for key in ("known_at", "cutoff"):
        if result[key] is not None:
            result[key] = datetime.fromisoformat(str(result[key]))
    for key in ("valid_from", "valid_to", "session"):
        if result[key] is not None:
            result[key] = date.fromisoformat(str(result[key]))
    result.update(record_id=canonical_sha256(payload), payload=payload, schema_version=1)
    return result


def audit(config_path: Path, input_run: str) -> tuple[int, Path]:
    config = load_history_config(config_path)
    parent, manifest = pinned_run(config, input_run)
    if manifest.command != "ingest" or manifest.config_sha256 != config.research_fingerprint():
        raise ValueError("audit requires matching pinned ingest run")
    bundle = HistoryBundle.model_validate_json((parent / "bundle.json").read_bytes())
    records = [
        RawRecord.model_validate(r) for r in json.loads((parent / "raw_index.json").read_bytes())
    ]
    validate_bundle(bundle, records, RawStore(config.paths.data_dir / "raw"))
    blockers = list(json.loads((parent / "blockers.json").read_bytes()))
    if (
        config.history.mode == "fixture"
        or bundle.prototype
        or any(r.source == "fixture" for r in records)
    ):
        blockers.append("prototype_only")
    if config.history.mode == "live":
        blockers.extend(pilot_blockers(config))
    if manifest.exit_code == 1:
        blockers.append("ingestion_failed")
    cutoffs = quarter_cutoffs(config.history.signal_start, config.history.signal_end)
    if not cutoffs:
        raise ValueError("history contains no quarter cutoffs")
    cells: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    discrepancies: list[dict[str, Any]] = []
    event_registry: list[dict[str, Any]] = []
    normalized_events: list[dict[str, Any]] = []
    for cutoff in cutoffs:
        universe, conflicts = resolve_universe(bundle, cutoff)
        market = market_filters(bundle, cutoff, universe)
        events, unresolved = normalize_events(bundle, cutoff)
        normalized_events.extend({"cutoff": cutoff.isoformat(), **r} for r in events)
        event_registry.extend({"cutoff": cutoff.isoformat(), **r} for r in unresolved)
        affected = {r["security_id"] for r in unresolved}
        for row in market:
            if row["security_id"] in affected:
                row["issues"].append("event_terms_unresolved")
                row["hard_filters_pass"] = False
            if row["group"] not in config.history.approved_groups:
                row["issues"].append("group_not_approved")
            cells.append({"cutoff": cutoff.isoformat(), **row})
        quarantine.extend({"cutoff": cutoff.isoformat(), **r} for r in conflicts)
        expected = bundle.independent_members.get(cutoff.date().isoformat())
        actual = {r["security_id"] for r in universe if r["membership"] == "verified"}
        if expected is None:
            discrepancies.append(
                {"cutoff": cutoff.isoformat(), "reason": "independent_universe_missing"}
            )
        else:
            for sid in sorted(set(expected) ^ actual):
                discrepancies.append(
                    {
                        "cutoff": cutoff.isoformat(),
                        "security_id": sid,
                        "reason": "independent_membership_discrepancy",
                    }
                )
        attestations = [
            r
            for r in asof(bundle.evidence, cutoff)
            if r.kind == "scope"
            and r.evidence_id in bundle.completeness_evidence_ids
            and r.attributes.get("completeness_verified") == "true"
            and r.attributes.get("independent_source")
            and r.attributes.get("independent_source") != r.source
            and r.attributes.get("reviewer")
        ]
        if not attestations:
            blockers.append("historical_completeness_not_certified")
        coverage.append(
            {
                "cutoff": cutoff.isoformat(),
                "candidates": len(universe),
                "verified_members": len(actual),
                "eligible_selected": sum(
                    r["hard_filters_pass"] and r["selected_class"] and not r["issues"]
                    for r in market
                ),
                "membership_counts": dict(Counter(r["membership"] for r in universe)),
                "reason_counts": dict(Counter(i for r in market for i in r["issues"])),
                "independent_denominator": len(expected) if expected is not None else None,
            }
        )
    for condition, reason in [
        (not cells, "historical_candidates_missing"),
        (bool(quarantine), "identity_conflicts"),
        (bool(discrepancies), "independent_universe_incomplete"),
        (bool(event_registry), "unresolved_events"),
        (
            any(
                set(r["issues"])
                - {
                    "adv20_below_threshold",
                    "raw_close_below_threshold",
                    "fewer_than_eight_reported_quarters",
                }
                and r["membership"] != "excluded"
                for r in cells
            ),
            "unresolved_candidate_data",
        ),
    ]:
        if condition:
            blockers.append(reason)
    earliest = min((r.valid_from for r in bundle.evidence if r.kind == "filing"), default=date.max)
    if earliest > config.history.warmup_start:
        blockers.append("warmup_coverage_unverified")
    if max((p.session for p in bundle.prices), default=date.min) < config.history.outcome_end:
        blockers.append("outcome_coverage_unverified")
    scope: dict[str, Any] = {
        "status": "prototype"
        if "prototype_only" in blockers
        else "blocked"
        if blockers
        else "approved",
        "approved": not blockers,
        "cutoffs": [c.isoformat() for c in cutoffs],
        "approved_groups": list(config.history.approved_groups),
        "mapping_version": bundle.mapping_version,
        "mapping_sha256": bundle.mapping_sha256,
        "historical_completeness": "unknown"
        if "historical_completeness_not_certified" in blockers
        else "verified",
        "blockers": sorted(set(blockers)),
        "performance_permitted": False,
    }
    run_id = new_run_id()
    temporary = Path(tempfile.mkdtemp(prefix=".audit-", dir=config.paths.artifact_dir))
    kinds = {
        "securities": "security",
        "identifier_history": "identifier",
        "memberships": "membership",
        "industry_history": "industry",
        "filings": "filing",
        "shares": "share",
    }
    hashes = {
        name: write_table(
            temporary, name, [r.model_dump(mode="json") for r in bundle.evidence if r.kind == kind]
        )
        for name, kind in kinds.items()
    }
    tables = {
        "corporate_actions": normalized_events,
        "entities": [{"entity_id": e} for e in sorted({r.entity_id for r in bundle.evidence})],
        "evidence": [r.model_dump(mode="json") for r in bundle.evidence],
        "prices": [p.model_dump(mode="json") for p in bundle.prices],
        "audit": cells,
        "scope": [scope],
    }
    hashes.update({name: write_table(temporary, name, rows) for name, rows in tables.items()})
    dump(
        temporary / "source_coverage.json",
        [
            {
                "source": source,
                "raw_records": sum(r.source == source for r in records),
                "evidence_records": sum(r.source == source for r in bundle.evidence),
            }
            for source in sorted({r.source for r in records} | {r.source for r in bundle.evidence})
        ],
    )
    for name, value in {
        "coverage": coverage,
        "quarantine": quarantine,
        "discrepancies": discrepancies,
        "unresolved_events": event_registry,
        "scope": scope,
        "blockers": scope["blockers"],
    }.items():
        dump(temporary / f"{name}.json", value)
    report = [
        "# Historical universe audit",
        "",
        f"Status: {scope['status']}; approved: {scope['approved']}.",
        "",
        "Coverage describes known candidates, not historical-universe completeness.",
        "",
        "| Cutoff | Candidates | Verified | Eligible selected |",
        "|---|---:|---:|---:|",
    ]
    report.extend(
        f"| {r['cutoff']} | {r['candidates']} | {r['verified_members']} | "
        f"{r['eligible_selected']} |"
        for r in coverage
    )
    report.extend(["", "## Blockers", *[f"- {b}" for b in scope["blockers"]]])
    (temporary / "audit.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    code = 3 if blockers else 0
    destination = publish(
        config,
        temporary,
        run_id,
        "audit-universe",
        code,
        input_run,
        {
            "parent_manifest": sha256_file(parent / "manifest.json"),
            "config": sha256_file(config_path),
        },
        hashes,
    )
    return code, destination
