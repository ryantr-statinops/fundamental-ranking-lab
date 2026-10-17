from datetime import UTC, date, datetime

import exchange_calendars as xcals
from tests.test_universe import bundle, evidence

from fundamental_ranking_lab.history_contracts import Price
from fundamental_ranking_lab.history_market import market_filters, normalize_events


def test_missing_prices_shares_and_quarters_are_explicit() -> None:
    result = market_filters(
        bundle([]),
        datetime(2010, 3, 31, 20, tzinfo=UTC),
        [{"security_id": "s", "entity_id": "e", "issues": []}],
    )
    assert not result[0]["hard_filters_pass"]
    assert "shares_unresolved" in result[0]["issues"]
    assert "class_selection_unresolved" in result[0]["issues"]


def test_events_require_verified_terms_and_effective_date() -> None:
    rows = [
        evidence(
            "event", "split", attributes={"action_type": "split", "ratio": "2", "verified": "true"}
        ),
        evidence("event", "delist", attributes={"action_type": "delisting"}),
        evidence("event", "future", valid_from="2015-01-01", attributes={"action_type": "merger"}),
    ]
    events, unresolved = normalize_events(bundle(rows), datetime(2010, 1, 1, tzinfo=UTC))
    assert len(events) == 2 and len(unresolved) == 1
    assert unresolved[0]["event_id"] == "delist"


def test_raw_and_adjusted_prices_are_distinct() -> None:
    row = Price(
        security_id="s",
        session=date(2010, 1, 4),
        known_at=datetime(2010, 1, 5, tzinfo=UTC),
        close="20",
        adjusted_close="10",
        volume="100",
        currency="USD",
        convention="unverified",
        raw_sha256="0" * 64,
    )
    assert row.close != row.adjusted_close


def test_adv_tie_break_missing_session_and_currency() -> None:
    cutoff = datetime(2010, 3, 31, 20, tzinfo=UTC)
    calendar = xcals.get_calendar("XNYS", start="2010-01-01", end="2010-12-31")
    sessions = calendar.sessions_in_range("2010-03-01", "2010-03-31")[-20:]
    rows = [
        evidence(
            "filing",
            f"q-{year}-{month}",
            attributes={"form": "10-Q", "period_end": f"{year}-{month:02d}-01"},
        )
        for year in (2007, 2008)
        for month in (3, 6, 9, 12)
    ]
    rows.extend(
        evidence("share", f"shares-{sid}", security_id=sid, attributes={"shares": "1000"})
        for sid in ("a", "b")
    )
    prices = [
        Price(
            security_id=sid,
            session=s.date(),
            known_at=s.to_pydatetime().replace(tzinfo=UTC),
            close="10",
            volume="100000",
            currency="USD",
            convention="verified_raw",
            raw_sha256="0" * 64,
        )
        for sid in ("a", "b")
        for s in sessions
    ]
    sample = bundle(rows).model_copy(update={"prices": tuple(prices)})
    universe = [{"security_id": sid, "entity_id": "e", "issues": []} for sid in ("a", "b")]
    result = market_filters(sample, cutoff, universe)
    assert all(r["hard_filters_pass"] for r in result)
    assert [r["security_id"] for r in result if r["selected_class"]] == ["a"]
    sample = sample.model_copy(update={"prices": tuple(prices[1:])})
    result = market_filters(sample, cutoff, universe)
    assert not any(r["selected_class"] for r in result)
    prices[0] = prices[0].model_copy(update={"currency": "EUR"})
    sample = sample.model_copy(update={"prices": tuple(prices)})
    assert "currency_unverified" in market_filters(sample, cutoff, universe)[0]["issues"]
