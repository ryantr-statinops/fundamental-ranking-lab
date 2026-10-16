from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

from fundamental_ranking_lab.features import (
    AccountingEvidence,
    Measure,
    compute_snapshot,
    quarters,
    select_as_of,
)
from fundamental_ranking_lab.filings import Fact


def fact(tag: str, value: int, end: date, start: date | None = None) -> Fact:
    return Fact(
        entity_id="fixture",
        accession=f"fixture-{end}",
        taxonomy="us-gaap",
        tag=tag,
        context_id=f"ctx-{start}-{end}",
        period_start=start,
        period_end=end,
        unit="USD",
        value_text=str(value),
        value=Decimal(value),
        filed_date=end + timedelta(days=30),
        published_at=datetime.combine(end + timedelta(days=30), datetime.min.time(), UTC),
        publication_precision="timestamp",
        raw_sha256="a" * 64,
        form="10-Q",
        document_period_end=end,
    )


def accounting_facts() -> list[Fact]:
    dates = [
        (date(2023, 10, 1), date(2023, 12, 31)),
        (date(2024, 1, 1), date(2024, 3, 31)),
        (date(2024, 4, 1), date(2024, 6, 30)),
        (date(2024, 7, 1), date(2024, 9, 30)),
        (date(2024, 10, 1), date(2024, 12, 31)),
        (date(2025, 1, 1), date(2025, 3, 31)),
        (date(2025, 4, 1), date(2025, 6, 30)),
        (date(2025, 7, 1), date(2025, 9, 30)),
    ]
    result = []
    for index, (start, end) in enumerate(dates):
        result.extend(
            [
                fact("Revenues", 100 + 10 * index, end, start),
                fact("NetIncomeLossAvailableToCommonStockholdersBasic", 10 + index, end, start),
            ]
        )
    for end, assets, equity in [(date(2024, 9, 30), 1000, 600), (date(2025, 9, 30), 1200, 800)]:
        result.extend(
            [
                fact("Assets", assets, end),
                fact("StockholdersEquity", equity, end),
                fact("PreferredStockValue", 0, end),
                fact("LongTermDebtCurrent", 10, end),
                fact("LongTermDebtNoncurrent", 90, end),
                fact("ShortTermBorrowings", 5, end),
            ]
        )
    return result


def test_eight_core_ratios_from_independent_numeric_fixture() -> None:
    snapshot = compute_snapshot(
        accounting_facts(),
        datetime(2025, 12, 31, 21, tzinfo=UTC),
        market_cap=Measure(value=Decimal(2000), lineage=("market",)),
        evidence=AccountingEvidence(debt_nonoverlap_verified=True, references=("verified-filing",)),
    )
    expected = {
        "roa": Decimal(62) / 1100,
        "roe": Decimal(62) / 700,
        "revenue_growth": Decimal(620) / 460 - 1,
        "earnings_growth": Decimal(62) / 46 - 1,
        "equity_ratio": Decimal(800) / 1200,
        "debt_ratio": Decimal(105) / 1200,
        "earnings_yield": Decimal(62) / 2000,
        "book_yield": Decimal(800) / 2000,
    }
    assert {name: value.value for name, value in snapshot.ratios.items()} == expected
    assert snapshot.valid_axes == 4 and snapshot.reports_available == 8
    assert all(value.lineage for value in snapshot.ratios.values())


def test_ytd_subtraction_and_direct_disagreement() -> None:
    start = date(2024, 1, 1)
    duration = {
        (start, date(2024, 3, 31)): Measure(value=Decimal(100)),
        (start, date(2024, 6, 30)): Measure(value=Decimal(250)),
        (start, date(2024, 9, 30)): Measure(value=Decimal(400)),
        (start, date(2024, 12, 31)): Measure(value=Decimal(800)),
    }
    assert [quarter.measure.value for quarter in quarters(duration)] == [100, 150, 150, 400]
    duration[date(2024, 4, 1), date(2024, 6, 30)] = Measure(value=Decimal(999))
    assert quarters(duration)[1].measure.reason == "quarter_reconciliation_mismatch"


def test_future_amendment_does_not_rewrite_past_snapshot() -> None:
    original = fact("Assets", 100, date(2025, 9, 30))
    amendment = original.model_copy(
        update={
            "value": Decimal(999),
            "accession": "amended",
            "published_at": datetime(2026, 1, 1, tzinfo=UTC),
        }
    )
    before, _ = select_as_of([original, amendment], datetime(2025, 12, 31, tzinfo=UTC))
    after, _ = select_as_of([original, amendment], datetime(2026, 1, 2, tzinfo=UTC))
    assert before[0].value == 100 and after[0].value == 999


def test_date_only_same_day_is_excluded_and_naive_cutoff_rejected() -> None:
    value = fact("Assets", 100, date(2025, 9, 30)).model_copy(update={"published_at": None})
    assert not value.available(datetime(2025, 10, 30, 22, tzinfo=UTC))
    assert value.available(datetime(2025, 10, 31, 22, tzinfo=UTC))
    with pytest.raises(ValueError, match="timezone-aware"):
        value.available(datetime(2025, 10, 31))


def test_negative_base_missing_debt_and_staleness_are_not_imputed() -> None:
    values = accounting_facts()
    values = [
        value.model_copy(update={"value": -abs(value.value)})
        if value.tag.startswith("NetIncomeLoss") and value.period_end < date(2024, 10, 1)
        else value
        for value in values
    ]
    snapshot = compute_snapshot(values, datetime(2025, 12, 31, tzinfo=UTC))
    assert snapshot.ratios["earnings_growth"].reason == "negative_base"
    assert snapshot.ratios["debt_ratio"].value is None
    stale = compute_snapshot(values, datetime(2026, 12, 31, tzinfo=UTC))
    assert all(value.reason == "stale" for value in stale.ratios.values())


def test_missing_quarter_does_not_shift_yoy_horizon() -> None:
    values = [value for value in accounting_facts() if value.period_end != date(2024, 12, 31)]
    snapshot = compute_snapshot(values, datetime(2025, 12, 31, tzinfo=UTC))
    assert snapshot.ratios["earnings_growth"].value is None
