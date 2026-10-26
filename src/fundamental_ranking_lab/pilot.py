"""Run the 160-cell feasibility pilot, preserving blockers and offline lineage."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import os
import platform
import re
import subprocess
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal
from zoneinfo import ZoneInfo

import exchange_calendars as xcals  # type: ignore[import-untyped]
import pyarrow as pa
from pydantic import Field

from fundamental_ranking_lab.config import StrictModel
from fundamental_ranking_lab.features import (
    RATIO_AXES,
    AccountingEvidence,
    Measure,
    compute_snapshot,
)
from fundamental_ranking_lab.filings import Fact, FilingHeader, parse_document, parse_header
from fundamental_ranking_lab.gates import assess_groups
from fundamental_ranking_lab.manifest import (
    RunManifest,
    canonical_sha256,
    new_run_id,
    sha256_file,
    write_manifest,
)
from fundamental_ranking_lab.pilot_config import (
    PilotConfig,
    RosterEntry,
    load_pilot_config,
    load_roster,
)
from fundamental_ranking_lab.pilot_schemas import FACTS_V2, RATIOS_V1
from fundamental_ranking_lab.providers import SECProvider, YFinanceProvider
from fundamental_ranking_lab.raw import RawRecord, RawStore, SecHTTP, SourceError, encode_json
from fundamental_ranking_lab.storage import write_parquet_atomic


class ClassEvidence(StrictModel):
    security_id: str
    symbol: str
    shares_raw_sha256: str
    shares_context_id: str


class CellEvidence(StrictModel):
    membership: Literal["member", "not_member", "unresolved"] = "unresolved"
    identity_verified: bool = False
    industry_verified: bool = False
    price_convention_verified: bool = False
    all_common_classes_verified: bool = False
    references: tuple[str, ...] = ()
    classes: tuple[ClassEvidence, ...] = ()
    accounting: AccountingEvidence = Field(default_factory=AccountingEvidence)


def cutoffs(years: tuple[int, ...]) -> list[datetime]:
    calendar = xcals.get_calendar("XNYS", start=f"{min(years)}-01-01", end=f"{max(years)}-12-31")
    result = []
    for year in years:
        sessions = calendar.sessions_in_range(f"{year}-12-01", f"{year}-12-31")
        day = sessions[-1].date()
        result.append(
            datetime(day.year, day.month, day.day, 16, tzinfo=ZoneInfo("America/New_York"))
        )
    return result


def _command_version(command: list[str]) -> str:
    try:
        return subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _source_tree_sha256(root: Path) -> str:
    """Hash tracked and untracked runtime sources as they exist for this run."""
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def _json(path: Path, value: object) -> None:
    with path.open("xb") as stream:
        stream.write(encode_json(value) + b"\n")


def _evidence(config: PilotConfig) -> dict[str, CellEvidence]:
    if config.pilot.evidence_path is None:
        return {}
    raw = json.loads(config.pilot.evidence_path.read_text(encoding="utf-8"))
    return {key: CellEvidence.model_validate(value) for key, value in raw.items()}


def _cell_evidence(
    entry: RosterEntry,
    cutoff: datetime,
    evidence: dict[str, CellEvidence],
    headers: dict[str, FilingHeader],
    records: list[RawRecord],
) -> CellEvidence:
    value = evidence.get(f"{entry.entity_id}:{cutoff.year}", CellEvidence())
    available = set()
    for record in records:
        header = headers.get(record.accession or "")
        if record.entity_id == entry.entity_id and header:
            published = header.published_at
            if published <= cutoff if published else header.filed_date < cutoff.date():
                available.add(record.sha256)
    references = (*value.references, *value.accounting.references)
    if not value.references or any(
        reference.split("#")[0] not in available for reference in references
    ):
        return CellEvidence()
    return value


def _market_data(
    entry: RosterEntry,
    cutoff: datetime,
    evidence: CellEvidence,
    facts: list[Fact],
    records: list[RawRecord],
    store: RawStore,
) -> tuple[Measure, dict[str, Any]]:
    missing = {
        "market_status": "class_or_price_evidence_unverified",
        "adv20": None,
        "selected_security_id": None,
        "price": None,
        "market_hard_filters": False,
    }
    if (
        not evidence.classes
        or not evidence.price_convention_verified
        or not evidence.identity_verified
        or not evidence.all_common_classes_verified
    ):
        return Measure(reason="common_class_market_cap_unverified"), missing
    calendar = xcals.get_calendar("XNYS", start=f"{cutoff.year}-01-01", end=f"{cutoff.year}-12-31")
    expected_sessions = {
        timestamp.date().isoformat()
        for timestamp in calendar.sessions_in_range(
            (cutoff.date() - timedelta(days=60)).isoformat(), cutoff.date().isoformat()
        )[-20:]
    }
    caps, candidates, lineage = [], [], []
    if len({item.security_id for item in evidence.classes}) != len(evidence.classes):
        return Measure(reason="duplicate_common_class"), missing
    for common_class in evidence.classes:
        shares = [
            fact
            for fact in facts
            if fact.available(cutoff)
            and fact.raw_sha256 == common_class.shares_raw_sha256
            and fact.context_id == common_class.shares_context_id
            and fact.tag == "EntityCommonStockSharesOutstanding"
            and fact.unit == "shares"
            and fact.period_start is None
            and 0 <= (cutoff.date() - fact.period_end).days <= 270
        ]
        if len(shares) != 1 or shares[0].value is None or shares[0].value <= 0:
            return Measure(reason="common_class_shares_unverified"), missing
        prices = []
        price_reference = ""
        for record in records:
            if record.entity_id != entry.entity_id or record.kind != "prices":
                continue
            payload = json.loads(store.read(record))
            if (
                payload["symbol"] == common_class.symbol
                and payload["cutoff"] == cutoff.date().isoformat()
            ):
                if payload.get("currency") != "USD":
                    return Measure(reason="price_currency_unverified"), missing
                prices = [row for row in payload["rows"] if row["date"] in expected_sessions]
                price_reference = record.sha256
                break
        if {row["date"] for row in prices} != expected_sessions or len(prices) != 20:
            return Measure(reason="missing_twenty_price_sessions"), missing
        if any(row.get("Close") is None or row.get("Volume") is None for row in prices):
            return Measure(reason="missing_price_or_volume"), missing
        closes = [Decimal(str(row["Close"])) for row in prices]
        volumes = [Decimal(str(row["Volume"])) for row in prices]
        if any(not value.is_finite() or value <= 0 for value in closes) or any(
            not value.is_finite() or value < 0 for value in volumes
        ):
            return Measure(reason="invalid_price_or_volume"), missing
        closing = Decimal(
            str(next(row["Close"] for row in prices if row["date"] == cutoff.date().isoformat()))
        )
        adv = (
            sum((close * volume for close, volume in zip(closes, volumes, strict=True)), Decimal(0))
            / 20
        )
        caps.append(shares[0].value * closing)
        candidates.append((adv, common_class.security_id, closing))
        lineage.extend(
            [
                price_reference,
                f"{shares[0].raw_sha256}#{shares[0].accession}#{shares[0].context_id}#{shares[0].taxonomy}:{shares[0].tag}",
            ]
        )
    chosen = sorted(candidates, key=lambda item: (-item[0], item[1]))[0]
    return Measure(value=sum(caps, Decimal(0)), lineage=tuple(lineage)), {
        "market_status": "verified",
        "adv20": str(chosen[0]),
        "selected_security_id": chosen[1],
        "price": str(chosen[2]),
        "market_hard_filters": chosen[0] >= 1_000_000 and chosen[2] >= 1,
    }


def _read_facts(
    records: list[RawRecord],
    roster: list[RosterEntry],
    store: RawStore,
) -> tuple[list[Fact], dict[str, FilingHeader], list[dict[str, str]]]:
    facts: list[Fact] = []
    headers: dict[str, FilingHeader] = {}
    issues = []
    entries = {entry.entity_id: entry for entry in roster}
    for record in records:
        if record.kind == "filing_text" and record.accession:
            try:
                headers[record.accession] = parse_header(store.read(record), record.accession)
            except ValueError:
                issues.append({"entity_id": record.entity_id, "reason": "invalid_filing_header"})
    filing_docs = [
        r for r in records if r.kind == "filing_document" and r.accession and r.accession in headers
    ]
    total_docs = len(filing_docs)
    print(f"Parsing {total_docs:,} filing documents into accounting facts...")
    for idx, record in enumerate(filing_docs, 1):
        assert record.accession is not None
        entry = entries[record.entity_id]
        parsed, problems = parse_document(
            store.read(record),
            entity_id=entry.entity_id,
            cik=entry.cik,
            header=headers[record.accession],
            raw_sha256=record.sha256,
        )
        facts.extend(parsed)
        issues.extend({"entity_id": entry.entity_id, "reason": problem} for problem in problems)
        if idx % 1000 == 0 or idx == total_docs:
            pct = f"{idx:,} / {total_docs:,}"
            print(f"  Parsed {pct} documents ({len(facts):,} facts extracted)...")
    unique = {canonical_sha256(fact.model_dump(mode="json")): fact for fact in facts}
    return [unique[key] for key in sorted(unique)], headers, issues


def _fact_rows(facts: list[Fact]) -> list[dict[str, Any]]:
    rows = []
    for fact in facts:
        row = fact.model_dump(exclude={"value", "dimensions"})
        row["normalized_decimal"] = str(fact.value) if fact.value is not None else None
        row["dimensions_json"] = json.dumps(fact.dimensions, separators=(",", ":"))
        rows.append(row)
    return rows


def run_pilot(config_path: Path, input_run: str | None = None) -> tuple[int, Path]:
    config = load_pilot_config(config_path)
    roster = load_roster(config.pilot.roster_path)
    evidence = _evidence(config)
    cutoff_values = cutoffs(config.pilot.years)
    if len(set(config.pilot.years)) != 4 or set(config.pilot.years) != {2012, 2018, 2022, 2025}:
        raise ValueError("the locked pilot requires cutoffs in 2012/2018/2022/2025")
    if input_run is not None and not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", input_run):
        raise ValueError("input_run must be a safe run identifier")
    run_id = new_run_id()
    root = config.paths.artifact_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    temporary = root / f".{run_id}.tmp"
    temporary.mkdir()
    store = RawStore(config.paths.data_dir / "raw")
    records: list[RawRecord] = []
    blockers: list[dict[str, str]] = []
    technical_failure = False
    roster_hash = sha256_file(config.pilot.roster_path)
    evidence_hash = (
        sha256_file(config.pilot.evidence_path)
        if config.pilot.evidence_path
        else canonical_sha256({})
    )
    _json(
        temporary / "selection.json",
        {
            "roster_sha256": roster_hash,
            "roster": [entry.model_dump(mode="json") for entry in roster],
            "cutoffs": [
                {"local": value.isoformat(), "utc": value.astimezone(UTC).isoformat()}
                for value in cutoff_values
            ],
            "reconciliation_rule": (
                "preselected entities; earliest actual member snapshot; no return selection"
            ),
            "evidence_status": "candidate flags require source verification; no returns inspected",
        },
    )
    try:
        if input_run:
            parent_path = root / input_run
            parent = RunManifest.model_validate_json(
                (parent_path / "manifest.json").read_text(encoding="utf-8")
            )
            if (
                parent.config_sha256 != config.research_fingerprint()
                or parent.input_artifacts.get("roster") != roster_hash
            ):
                raise SourceError(
                    "replay research config or frozen roster differs from the parent run"
                )
            if parent.input_artifacts.get("evidence") != evidence_hash:
                raise SourceError("replay evidence differs from the parent run")
            index = parent_path / "raw_index.json"
            if sha256_file(index) != parent.output_artifacts.get("raw_index.json"):
                raise SourceError("parent raw index checksum mismatch")
            records = [
                RawRecord.model_validate(row)
                for row in json.loads(index.read_text(encoding="utf-8"))
            ]
            for record in records:
                store.read(record)
        else:
            user_agent = os.environ.get(config.provider.sec_user_agent_env, "")
            if not user_agent.strip():
                blockers.append({"entity_id": "all", "reason": "sec_contact_not_configured"})
            else:
                http = SecHTTP(user_agent, config.collection)
                provider = SECProvider(http, store)
                try:
                    for entry in roster:
                        try:
                            provider.collect(entry, config.pilot.years)
                        except SourceError as exc:
                            blockers.append({"entity_id": entry.entity_id, "reason": str(exc)})
                            technical_failure |= "404" not in str(exc)
                        if http.disabled:
                            break
                finally:
                    records = provider.records
                    http.close()
                blockers.extend(provider.issues)
        facts, headers, parse_issues = _read_facts(records, roster, store)
        blockers.extend(parse_issues)
        if not input_run and records:
            prices = YFinanceProvider(store, config.collection.requests_per_second)
            for entry in roster:
                for cutoff in cutoff_values:
                    cell_evidence = _cell_evidence(entry, cutoff, evidence, headers, records)
                    if cell_evidence.identity_verified and cell_evidence.classes:
                        for common_class in cell_evidence.classes:
                            try:
                                records.append(
                                    prices.collect(entry, common_class.symbol, cutoff.date())
                                )
                            except Exception:
                                blockers.append(
                                    {
                                        "entity_id": entry.entity_id,
                                        "reason": "yfinance_collection_failed",
                                    }
                                )
                                technical_failure = True
        coverage: list[dict[str, Any]] = []
        ratio_rows: list[dict[str, Any]] = []
        for entry in roster:
            entity_facts = [fact for fact in facts if fact.entity_id == entry.entity_id]
            for cutoff in cutoff_values:
                proof = _cell_evidence(entry, cutoff, evidence, headers, records)
                cap, market = _market_data(entry, cutoff, proof, entity_facts, records, store)
                snapshot = compute_snapshot(
                    entity_facts, cutoff, market_cap=cap, evidence=proof.accounting
                )
                actual = (
                    proof.membership == "member"
                    and proof.identity_verified
                    and proof.industry_verified
                    and snapshot.period_end is not None
                )
                hard_filters = (
                    actual and snapshot.reports_available >= 8 and market["market_hard_filters"]
                )
                coverage.append(
                    {
                        "entity_id": entry.entity_id,
                        "group": entry.group,
                        "cutoff": cutoff.isoformat(),
                        "membership": proof.membership,
                        "identity_verified": proof.identity_verified,
                        "industry_verified": proof.industry_verified,
                        "actual_snapshot": actual,
                        "reports_available": snapshot.reports_available,
                        "hard_filters": hard_filters,
                        "period_end": snapshot.period_end.isoformat()
                        if snapshot.period_end
                        else None,
                        "valid_ratios": sum(
                            value.value is not None for value in snapshot.ratios.values()
                        ),
                        "valid_axes": snapshot.valid_axes,
                        "eligible": hard_filters and snapshot.valid_axes >= 3,
                        "status": "not_member"
                        if proof.membership == "not_member"
                        else "usable"
                        if actual
                        else "unresolved",
                        "axis_coverage": snapshot.axis_coverage,
                        "issues": snapshot.issues,
                        **market,
                    }
                )
                for name, value in snapshot.ratios.items():
                    ratio_rows.append(
                        {
                            "entity_id": entry.entity_id,
                            "cutoff": cutoff.astimezone(UTC),
                            "ratio": name,
                            "axis": RATIO_AXES[name],
                            "value_decimal": str(value.value) if value.value is not None else None,
                            "missing_reason": value.reason,
                            "lineage": list(value.lineage),
                        }
                    )
        _json(temporary / "coverage.json", coverage)
        _json(temporary / "raw_index.json", [record.model_dump(mode="json") for record in records])
        _json(temporary / "blockers.json", blockers)
        fact_rows = _fact_rows(facts)
        write_parquet_atomic(
            pa.Table.from_pylist(fact_rows, schema=FACTS_V2), temporary / "facts.parquet", FACTS_V2
        )
        write_parquet_atomic(
            pa.Table.from_pylist(ratio_rows, schema=RATIOS_V1),
            temporary / "ratios.parquet",
            RATIOS_V1,
        )
        content_hashes = {
            "facts": canonical_sha256(fact_rows),
            "ratios": canonical_sha256(ratio_rows),
            "coverage": canonical_sha256(coverage),
        }
        _write_reconciliation(temporary, roster, coverage, ratio_rows, facts)
        approved_groups, review_issues = _read_review(
            config, input_run, content_hashes, temporary, coverage
        )
        blockers.extend(review_issues)
        all_have_snapshot = all(
            any(
                cell["entity_id"] == entry.entity_id and cell["actual_snapshot"]
                for cell in coverage
            )
            for entry in roster
        )
        gates = assess_groups(coverage, approved_groups, all_have_snapshot=all_have_snapshot)
        _json(temporary / "group_gates.json", gates)
        _json(temporary / "blockers_final.json", blockers)
        exit_code = (
            1
            if technical_failure
            else 0
            if all_have_snapshot and all(gate["status"] == "pass" for gate in gates)
            else 3
        )
        _write_report(temporary, run_id, coverage, gates, blockers, content_hashes)
    except Exception as exc:
        exit_code = 1
        content_hashes = {}
        # Do not persist exception text: third-party exceptions can embed private request headers.
        _json(temporary / "failure.json", {"error_type": type(exc).__name__, "status": "failed"})
        if not (temporary / "raw_index.json").exists():
            _json(
                temporary / "raw_index.json", [record.model_dump(mode="json") for record in records]
            )
        if not (temporary / "feasibility.md").exists():
            failure_report = (
                "# Pilot failed\n\nNo group was approved. See failure.json "
                "and the pinned raw index.\n"
            )
            (temporary / "feasibility.md").write_text(failure_report, encoding="utf-8")
            (temporary / "feasibility.html").write_text(
                '<!doctype html><html lang="en"><meta charset="utf-8">'
                "<title>Pilot failure report</title><body><pre>"
                + html.escape(failure_report)
                + "</pre></body></html>\n",
                encoding="utf-8",
            )
    _json(
        temporary / "log.jsonl",
        {"event": "pilot_finished", "run_id": run_id, "exit_code": exit_code},
    )
    outputs = {path.name: sha256_file(path) for path in temporary.iterdir() if path.is_file()}
    manifest = RunManifest(
        run_id=run_id,
        created_at_utc=datetime.now(UTC),
        command="pilot",
        manifest_version=2,
        config_sha256=config.research_fingerprint(),
        execution_sha256=config.execution_fingerprint(),
        code_revision=_command_version(["git", "rev-parse", "HEAD"]),
        code_sha256=_source_tree_sha256(Path("src/fundamental_ranking_lab")),
        lockfile_sha256=sha256_file(Path("uv.lock")) if Path("uv.lock").exists() else None,
        tool_versions={
            "python": platform.python_version(),
            "uv": _command_version(["uv", "--version"]),
        },
        schema_versions={"facts": "2", "ratios": "1"},
        factor_version=config.pilot.factor_version,
        mapping_version=config.pilot.mapping_version,
        parent_run=input_run,
        status="approved" if exit_code == 0 else "failed" if exit_code == 1 else "blocked",
        exit_code=exit_code,
        input_artifacts={
            "roster": roster_hash,
            "evidence": evidence_hash,
            "config_file": sha256_file(config_path),
            **(
                {"review": sha256_file(config.pilot.review_path)}
                if config.pilot.review_path
                else {}
            ),
            **{record.relative_path: record.sha256 for record in records},
        },
        output_artifacts=outputs,
        content_hashes=content_hashes,
    )
    write_manifest(manifest, temporary / "manifest.json")
    destination = root / run_id
    os.rename(temporary, destination)
    return exit_code, destination


def _write_reconciliation(
    directory: Path,
    roster: list[RosterEntry],
    coverage: list[dict[str, Any]],
    ratios: list[dict[str, Any]],
    facts: list[Fact],
) -> None:
    fields = [
        "entity_id",
        "group",
        "cutoff",
        "kind",
        "name",
        "expected",
        "actual",
        "difference",
        "tolerance",
        "allowed_tolerance",
        "missing_reason",
        "unit",
        "scale",
        "period_start",
        "period_end",
        "source_ref",
        "reviewer",
        "reviewed_at",
        "status",
    ]
    with (directory / "reconciliation.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for entry in roster:
            if not entry.reconcile:
                continue
            actual_cells = [
                cell
                for cell in coverage
                if cell["entity_id"] == entry.entity_id and cell["actual_snapshot"]
            ]
            selected = min(actual_cells, key=lambda cell: cell["cutoff"]) if actual_cells else None
            if selected is None:
                writer.writerow(
                    {
                        "entity_id": entry.entity_id,
                        "group": entry.group,
                        "kind": "snapshot",
                        "status": "blocked_no_actual_snapshot",
                    }
                )
                continue
            selected_cutoff = datetime.fromisoformat(selected["cutoff"])
            cell_ratios = [
                row
                for row in ratios
                if row["entity_id"] == entry.entity_id and row["cutoff"] == selected_cutoff
            ]
            references = {ref for row in cell_ratios for ref in row["lineage"]}
            for row in cell_ratios:
                writer.writerow(
                    {
                        "entity_id": entry.entity_id,
                        "group": entry.group,
                        "cutoff": selected["cutoff"],
                        "kind": "ratio",
                        "name": row["ratio"],
                        "actual": row["value_decimal"],
                        "allowed_tolerance": "0.000000000001",
                        "missing_reason": row["missing_reason"],
                        "unit": "pure",
                        "source_ref": "|".join(row["lineage"]),
                        "status": "pending_independent_check",
                    }
                )
            for fact in facts:
                ref = (
                    f"{fact.raw_sha256}#{fact.accession}#{fact.context_id}"
                    f"#{fact.taxonomy}:{fact.tag}"
                )
                if ref in references:
                    tolerance = Decimal(0)
                    if (
                        fact.decimals
                        and fact.decimals.lstrip("-").isdigit()
                        and abs(int(fact.decimals)) < 100
                    ):
                        tolerance = Decimal(10) ** -int(fact.decimals) / 2
                    writer.writerow(
                        {
                            "entity_id": entry.entity_id,
                            "group": entry.group,
                            "cutoff": selected["cutoff"],
                            "kind": "input",
                            "name": fact.tag,
                            "unit": fact.unit,
                            "scale": fact.scale,
                            "period_start": fact.period_start,
                            "period_end": fact.period_end,
                            "allowed_tolerance": str(tolerance),
                            "actual": str(fact.value),
                            "source_ref": ref,
                            "status": "pending_independent_check",
                        }
                    )


def _read_review(
    config: PilotConfig,
    parent: str | None,
    hashes: dict[str, str],
    directory: Path,
    coverage: list[dict[str, Any]],
) -> tuple[set[str], list[dict[str, str]]]:
    if config.pilot.review_path is None:
        return set(), [
            {"entity_id": "all", "reason": "independent_reconciliation_and_user_review_pending"}
        ]
    from fundamental_ranking_lab.review import validate_review

    try:
        return validate_review(config.pilot.review_path, parent, hashes, directory, coverage)
    except (ValueError, KeyError, TypeError, OSError, AttributeError):
        return set(), [{"entity_id": "all", "reason": "invalid_review_file"}]


def _write_report(
    directory: Path,
    run_id: str,
    coverage: list[dict[str, Any]],
    gates: list[dict[str, Any]],
    blockers: list[dict[str, str]],
    hashes: dict[str, str],
) -> None:
    lines = [
        "# Pilot feasibility report",
        "",
        f"Run: {run_id}",
        "",
        (
            f"Cells: {len(coverage)}; actual snapshots: "
            f"{sum(cell['actual_snapshot'] for cell in coverage)}."
        ),
        "",
        (
            "This is a data-feasibility pilot. It establishes neither a survivor-free universe "
            "nor investment performance."
        ),
        "",
        "| Group | Status | Actual entities | Covered / member snapshots |",
        "|---|---|---:|---:|",
    ]
    lines.extend(
        (
            f"| {gate['group']} | {gate['status']} | {gate['actual_entities']} | "
            f"{gate['covered_member_snapshots']} / {gate['member_snapshots']} |"
        )
        for gate in gates
    )
    lines.extend(["", "## Blockers", ""])
    lines.extend(f"- {item['entity_id']}: {item['reason']}" for item in blockers)
    lines.extend(
        [
            "",
            "## Pinned content hashes",
            "",
            *[f"- {key}: {value}" for key, value in hashes.items()],
            "",
        ]
    )
    report = "\n".join(lines)
    (directory / "feasibility.md").write_text(report, encoding="utf-8")
    (directory / "feasibility.html").write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        "<title>Pilot feasibility report</title><body><pre>"
        + html.escape(report)
        + "</pre></body></html>\n",
        encoding="utf-8",
    )
