from datetime import UTC, datetime

from fundamental_ranking_lab.history_contracts import Evidence, HistoryBundle
from fundamental_ranking_lab.manifest import canonical_sha256
from fundamental_ranking_lab.universe import asof, resolve_universe


def evidence(kind: str, eid: str, **changes: object) -> Evidence:
    row = dict(
        kind=kind,
        evidence_id=eid,
        revision_id="1",
        entity_id="e",
        security_id="s",
        source="fixture",
        source_record_id=eid,
        raw_sha256="0" * 64,
        known_at="2009-01-01T00:00:00Z",
        valid_from="2009-01-01",
        attributes={},
    )
    return Evidence.model_validate({**row, **changes})


def bundle(rows: list[Evidence]) -> HistoryBundle:
    mapping = [{"low": 100, "high": 5999, "industry": "Other", "group": "General"}]
    return HistoryBundle.model_validate(
        dict(
            mapping_version="test",
            mapping=mapping,
            mapping_sha256=canonical_sha256(mapping),
            evidence=rows,
        )
    )


def test_revision_and_future_evidence_do_not_rewrite_past() -> None:
    original = evidence("identifier", "ticker", attributes={"type": "ticker", "value": "OLD"})
    correction = original.model_copy(
        update={
            "revision_id": "2",
            "known_at": datetime(2012, 1, 1, tzinfo=UTC),
            "attributes": {"type": "ticker", "value": "NEW"},
        }
    )
    assert asof((original, correction), datetime(2010, 1, 1, tzinfo=UTC))[0] == original
    assert asof((original, correction), datetime(2013, 1, 1, tzinfo=UTC))[0] == correction


def test_identity_listing_and_sic_require_evidence() -> None:
    rows = [
        evidence(
            "security",
            "security",
            attributes={
                "country": "US",
                "security_type": "common",
                "exchange": "NYSE",
                "share_class": "A",
            },
        ),
        evidence("identifier", "ticker", attributes={"type": "ticker", "value": "ABC"}),
        evidence("membership", "listing", attributes={"verified": "true"}),
        evidence("industry", "sic", attributes={"sic": "6798"}),
    ]
    cutoff = datetime(2010, 1, 1, tzinfo=UTC)
    result, quarantine = resolve_universe(bundle(rows), cutoff)
    assert result[0]["membership"] == "verified"
    assert result[0]["group"] == "REIT"
    assert not quarantine
    result, _ = resolve_universe(bundle(rows[:-1]), cutoff)
    assert result[0]["membership"] == "unresolved"
    rows.append(
        evidence("identifier", "ticker-conflict", attributes={"type": "ticker", "value": "XYZ"})
    )
    result, quarantine = resolve_universe(bundle(rows), cutoff)
    assert quarantine and result[0]["membership"] == "unresolved"


def test_ticker_reuse_is_allowed_only_in_nonoverlapping_intervals() -> None:
    first = evidence(
        "identifier", "first", attributes={"type": "ticker", "value": "ABC"}, valid_to="2011-01-01"
    )
    second = evidence(
        "identifier",
        "second",
        security_id="s2",
        valid_from="2011-01-01",
        attributes={"type": "ticker", "value": "ABC"},
    )
    assert len(asof((first, second), datetime(2010, 1, 1, tzinfo=UTC))) == 1
    assert asof((first, second), datetime(2012, 1, 1, tzinfo=UTC))[0].security_id == "s2"


def test_duplicate_entity_class_and_overlapping_ticker_are_quarantined() -> None:
    rows = []
    for sid in ("s", "s2"):
        rows.extend(
            [
                evidence(
                    "security",
                    f"security-{sid}",
                    security_id=sid,
                    attributes={
                        "country": "US",
                        "security_type": "common",
                        "exchange": "NYSE",
                        "share_class": "A",
                    },
                ),
                evidence(
                    "identifier",
                    f"ticker-{sid}",
                    security_id=sid,
                    attributes={"type": "ticker", "value": "SAME"},
                ),
            ]
        )
    output, quarantine = resolve_universe(bundle(rows), datetime(2010, 1, 1, tzinfo=UTC))
    assert len(quarantine) == 2
    assert all(r["membership"] == "unresolved" for r in output)
