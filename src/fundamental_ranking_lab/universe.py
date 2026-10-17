"""Evidence-driven identity and universe decisions at a historical cutoff."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Any

from fundamental_ranking_lab.history_contracts import Evidence, HistoryBundle


def asof(rows: tuple[Evidence, ...], cutoff: datetime) -> list[Evidence]:
    revisions: dict[str, Evidence] = {}
    for row in rows:
        if row.known_at > cutoff:
            continue
        previous = revisions.get(row.evidence_id)
        if previous is not None and row.known_at == previous.known_at:
            raise ValueError("ambiguous evidence revisions at identical known_at")
        if previous is None or row.known_at > previous.known_at:
            revisions[row.evidence_id] = row
    return sorted(
        (
            row
            for row in revisions.values()
            if row.valid_from <= cutoff.date()
            and (row.valid_to is None or cutoff.date() < row.valid_to)
        ),
        key=lambda row: row.evidence_id,
    )


def resolve_universe(
    bundle: HistoryBundle, cutoff: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    rows = asof(bundle.evidence, cutoff)
    quarantine: list[dict[str, str]] = []
    securities = [row for row in rows if row.kind == "security"]
    grouped: dict[str, list[Evidence]] = defaultdict(list)
    tickers: dict[str, set[str]] = defaultdict(set)
    classes: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in securities:
        assert row.security_id is not None
        grouped[row.security_id].append(row)
        classes[row.entity_id, row.attributes.get("share_class", "")].add(row.security_id)
    for row in rows:
        if row.kind == "identifier" and row.attributes.get("type") == "ticker":
            assert row.security_id is not None
            tickers[row.attributes["value"]].add(row.security_id)
    conflicting = {sid for ids in tickers.values() if len(ids) > 1 for sid in ids}
    conflicting.update(sid for ids in classes.values() if len(ids) > 1 for sid in ids)
    output = []
    for sid, definitions in sorted(grouped.items()):
        security = definitions[0]
        issues: list[str] = []
        if len(definitions) != 1 or sid in conflicting:
            issues.append("identity_conflict")
        identifiers = [r for r in rows if r.kind == "identifier" and r.security_id == sid]
        ticker_rows = [r for r in identifiers if r.attributes.get("type") == "ticker"]
        if len(ticker_rows) != 1:
            issues.append("ticker_missing_or_conflicting")
        membership = [r for r in rows if r.kind == "membership" and r.security_id == sid]
        if (
            len(membership) != 1
            or membership[0].attributes.get("verified") != "true"
            or membership[0].source in {"yfinance", "stooq"}
        ):
            issues.append("listing_unverified")
        attrs = security.attributes
        status = "verified"
        if not all(
            attrs.get(key) for key in ("country", "security_type", "exchange", "share_class")
        ):
            issues.append("security_classification_unresolved")
        elif attrs.get("country") != "US" or attrs.get("security_type") != "common":
            status = "excluded"
            issues.append("country_or_security_type_excluded")
        elif attrs.get("exchange") not in {"NYSE", "NASDAQ", "AMEX"}:
            status = "excluded"
            issues.append("exchange_excluded")
        industry = [r for r in rows if r.kind == "industry" and r.entity_id == security.entity_id]
        group, industry_code = None, None
        if len(industry) == 1 and industry[0].attributes.get("sic", "").isdigit():
            sic = int(industry[0].attributes["sic"])
            matches = [m for m in bundle.mapping if m.low <= sic <= m.high]
            if sic == 6798:
                group, industry_code = "REIT", "Finan"
            elif len(matches) == 1:
                group, industry_code = matches[0].group, matches[0].industry
            else:
                issues.append("industry_mapping_missing_or_conflicting")
        else:
            issues.append("historical_sic_unresolved")
        if issues and status != "excluded":
            status = "unresolved"
        if any("conflict" in issue for issue in issues):
            quarantine.append({"security_id": sid, "reason": ";".join(issues)})
        output.append(
            {
                "security_id": sid,
                "entity_id": security.entity_id,
                "ticker": ticker_rows[0].attributes["value"] if len(ticker_rows) == 1 else None,
                "group": group,
                "industry": industry_code,
                "membership": status,
                "issues": issues,
                "evidence_ids": [
                    r.evidence_id
                    for r in rows
                    if r.security_id == sid or r.entity_id == security.entity_id
                ],
            }
        )
    # Preserve candidates whose identifiers/listing evidence exist without a security definition.
    for sid in sorted({r.security_id for r in rows if r.security_id} - set(grouped)):
        related = [r for r in rows if r.security_id == sid]
        output.append(
            {
                "security_id": sid,
                "entity_id": related[0].entity_id,
                "ticker": None,
                "group": None,
                "industry": None,
                "membership": "unresolved",
                "issues": ["security_definition_missing"],
                "evidence_ids": [r.evidence_id for r in related],
            }
        )
    return output, quarantine
