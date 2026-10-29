from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from fundamental_ranking_lab.filings import FilingHeader, parse_document, parse_header


def test_original_xbrl_preserves_period_unit_context_and_source() -> None:
    content = (Path(__file__).parent / "fixtures/pilot/as-filed.xml").read_bytes()
    header = FilingHeader(accession="fixture", filed_date=date(2025, 11, 1), form="10-Q")
    facts, issues = parse_document(
        content, entity_id="fixture", cik="0000000001", header=header, raw_sha256="a" * 64
    )
    assert not issues
    revenue = next(fact for fact in facts if fact.tag == "Revenues")
    assert revenue.value == Decimal(170)
    assert revenue.period_start == date(2025, 7, 1)
    assert revenue.unit == "USD" and revenue.context_id == "duration"
    assert revenue.raw_sha256 == "a" * 64
    assert revenue.document_period_end == date(2025, 9, 30)
    assert not revenue.available(datetime(2025, 11, 1, 16, tzinfo=ZoneInfo("America/New_York")))
    assert revenue.available(datetime(2025, 11, 2, 16, tzinfo=ZoneInfo("America/New_York")))


@pytest.mark.parametrize(("accepted", "utc_hour"), [("20250701160000", 20), ("20251231160000", 21)])
def test_original_acceptance_header_uses_eastern_dst(accepted: str, utc_hour: int) -> None:
    content = (
        f"<ACCEPTANCE-DATETIME>{accepted}\nFILED AS OF DATE: {accepted[:8]}\n"
        "CONFORMED SUBMISSION TYPE: 10-Q\n"
        "STANDARD INDUSTRIAL CLASSIFICATION: TEST [3571]"
    ).encode()
    header = parse_header(content, "fixture")
    assert header.published_at is not None
    assert header.published_at.hour == utc_hour
    assert header.published_at.tzinfo == UTC
    assert header.sic == "3571"


def test_inline_scale_sign_and_custom_context_are_preserved() -> None:
    content = b"""<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance">
    <xbrli:context id="i"><xbrli:entity><xbrli:identifier>1</xbrli:identifier></xbrli:entity>
    <xbrli:period><xbrli:instant>2025-09-30</xbrli:instant></xbrli:period></xbrli:context>
    <xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
    <ix:nonFraction name="custom:Metric" contextRef="i" unitRef="USD" scale="3" sign="-"
    format="ixt:num-dot-decimal">1,234</ix:nonFraction></html>"""
    facts, issues = parse_document(
        content,
        entity_id="fixture",
        cik="0000000001",
        header=FilingHeader(accession="f", filed_date=date(2025, 10, 1), form="10-Q"),
        raw_sha256="b" * 64,
    )
    assert not issues
    assert facts[0].value == Decimal(-1_234_000)
    assert facts[0].taxonomy == "custom" and facts[0].scale == 3


def test_inline_numdotdecimal_and_zerodash_transforms_are_supported() -> None:
    content = b"""<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xbrli="http://www.xbrl.org/2003/instance">
    <xbrli:context id="i"><xbrli:entity><xbrli:identifier>1</xbrli:identifier></xbrli:entity>
    <xbrli:period><xbrli:instant>2025-09-30</xbrli:instant></xbrli:period></xbrli:context>
    <xbrli:unit id="USD"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
    <ix:nonFraction name="us-gaap:Assets" contextRef="i" unitRef="USD" scale="6"
    format="ixt:numdotdecimal">1,234.56</ix:nonFraction>
    <ix:nonFraction name="us-gaap:ShortTermBorrowings" contextRef="i" unitRef="USD" scale="6"
    format="ixt:zerodash">-</ix:nonFraction></html>"""
    facts, issues = parse_document(
        content,
        entity_id="fixture",
        cik="0000000001",
        header=FilingHeader(accession="f", filed_date=date(2025, 10, 1), form="10-Q"),
        raw_sha256="c" * 64,
    )
    assert not issues
    assert len(facts) == 2
    assert facts[0].value == Decimal("1234560000")
    assert facts[1].value == Decimal(0)
