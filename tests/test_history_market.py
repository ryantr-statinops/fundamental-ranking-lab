from datetime import UTC, date, datetime

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
