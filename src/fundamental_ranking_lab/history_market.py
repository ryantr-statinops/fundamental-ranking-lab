"""Historical market filters with explicit price conventions and event uncertainty."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

import exchange_calendars as xcals  # type: ignore[import-untyped]

from fundamental_ranking_lab.history_contracts import HistoryBundle, Price
from fundamental_ranking_lab.universe import asof


def market_filters(
    bundle: HistoryBundle, cutoff: datetime, universe: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    calendar = xcals.get_calendar(
        "XNYS", start=f"{cutoff.year - 1}-01-01", end=f"{cutoff.year + 1}-12-31"
    )
    sessions = calendar.sessions_in_range(f"{cutoff.year - 1}-12-01", cutoff.date().isoformat())
    expected = {s.date() for s in sessions[-20:]}
    evidence = asof(bundle.evidence, cutoff)
    results = []
    for security in universe:
        sid, entity = security["security_id"], security["entity_id"]
        issues = list(security["issues"])
        prices = [
            p
            for p in bundle.prices
            if p.security_id == sid and p.session in expected and p.known_at <= cutoff
        ]
        by_session: dict[object, list[Price]] = defaultdict(list)
        for price in prices:
            by_session[price.session].append(price)
        if set(by_session) != expected or any(len(p) != 1 for p in by_session.values()):
            issues.append("missing_or_duplicate_price_session")
        if any(p.currency != "USD" for p in prices):
            issues.append("currency_unverified")
        if {p.convention for p in prices} != {"verified_raw"}:
            issues.append("price_convention_unverified")
        adv = None
        if not any(
            i in issues
            for i in (
                "missing_or_duplicate_price_session",
                "currency_unverified",
                "price_convention_unverified",
            )
        ):
            adv = sum((p.close * p.volume for p in prices), Decimal(0)) / 20
            if adv < Decimal(1_000_000):
                issues.append("adv20_below_threshold")
            if max(prices, key=lambda p: p.session).close < 1:
                issues.append("raw_close_below_threshold")
        filings = {
            r.attributes["period_end"]
            for r in evidence
            if r.entity_id == entity
            and r.kind == "filing"
            and r.attributes.get("form") in {"10-K", "10-Q", "10-K/A", "10-Q/A"}
            and r.attributes.get("period_end")
        }
        filings = {period for period in filings if date.fromisoformat(period) <= cutoff.date()}
        quarters = {
            (date.fromisoformat(period).year, (date.fromisoformat(period).month - 1) // 3)
            for period in filings
        }
        if len(quarters) < 8:
            issues.append("fewer_than_eight_reported_quarters")
        shares = [r for r in evidence if r.security_id == sid and r.kind == "share"]
        try:
            latest = max(shares, key=lambda r: (r.valid_from, r.known_at))
            count = Decimal(latest.attributes["shares"])
            if not count.is_finite() or count <= 0:
                raise ValueError("invalid shares")
        except (ValueError, KeyError, InvalidOperation):
            issues.append("shares_unresolved")
        results.append(
            {
                **security,
                "issues": sorted(set(issues)),
                "adv20_usd": str(adv) if adv is not None else None,
                "reported_quarters": len(quarters),
                "selected_class": False,
                "hard_filters_pass": not issues,
            }
        )
    # Select before hard filters: never substitute a less-liquid class because the winner failed.
    by_entity: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in results:
        by_entity[row["entity_id"]].append(row)
    for classes in by_entity.values():
        if any(row["adv20_usd"] is None for row in classes):
            for row in classes:
                row["issues"].append("class_selection_unresolved")
                row["hard_filters_pass"] = False
            continue
        winner = min(classes, key=lambda r: (-Decimal(r["adv20_usd"]), r["security_id"]))
        winner["selected_class"] = True
    return results


def normalize_events(
    bundle: HistoryBundle, cutoff: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    events, unresolved = [], []
    for row in asof(bundle.evidence, cutoff):
        if row.kind != "event":
            continue
        attrs = row.attributes
        kind = attrs.get("action_type")
        ready = attrs.get("verified") == "true" and kind in {
            "split",
            "dividend",
            "merger",
            "delisting",
            "recovery",
        }
        if kind == "split":
            try:
                ratio = Decimal(attrs.get("ratio", "NaN"))
                ready = ready and ratio.is_finite() and ratio > 0
            except InvalidOperation:
                ready = False
        if kind in {"dividend", "recovery"}:
            try:
                amount = Decimal(attrs.get("cash_amount", "NaN"))
                ready = (
                    ready and amount.is_finite() and amount >= 0 and attrs.get("currency") == "USD"
                )
            except InvalidOperation:
                ready = False
        if kind in {"merger", "delisting"}:
            ready = ready and attrs.get("terms_verified") == "true"
        events.append({**row.model_dump(mode="json"), "resolved": ready})
        if not ready:
            unresolved.append(
                {
                    "security_id": str(row.security_id),
                    "event_id": row.evidence_id,
                    "reason": "event_terms_unresolved",
                }
            )
    return events, unresolved
