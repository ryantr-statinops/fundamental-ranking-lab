"""Conservative as-filed period construction and the eight locked core ratios."""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from pydantic import Field

from fundamental_ranking_lab.config import StrictModel
from fundamental_ranking_lab.filings import Fact

REVENUE_TAGS = (
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
)
COMMON_NI = "NetIncomeLossAvailableToCommonStockholdersBasic"
RATIO_AXES = {
    "roa": "quality",
    "roe": "quality",
    "revenue_growth": "growth",
    "earnings_growth": "growth",
    "equity_ratio": "financial_health",
    "debt_ratio": "financial_health",
    "earnings_yield": "valuation",
    "book_yield": "valuation",
}


class Measure(StrictModel):
    value: Decimal | None = None
    reason: str | None = None
    lineage: tuple[str, ...] = ()


class Quarter(StrictModel):
    start: date
    end: date
    measure: Measure


class AccountingEvidence(StrictModel):
    no_preferred: bool = False
    no_preferred_period_ends: tuple[date, ...] = ()
    debt_nonoverlap_verified: bool = False
    references: tuple[str, ...] = ()


class RatioSnapshot(StrictModel):
    ratios: dict[str, Measure]
    period_end: date | None
    valid_axes: int
    reports_available: int
    issues: tuple[str, ...] = ()
    axis_coverage: dict[str, int] = Field(default_factory=dict)


def _reference(fact: Fact) -> str:
    return f"{fact.raw_sha256}#{fact.accession}#{fact.context_id}#{fact.taxonomy}:{fact.tag}"


def _publication_order(fact: Fact) -> datetime:
    return fact.published_at or datetime.combine(
        fact.filed_date, time.max, ZoneInfo("America/New_York")
    ).astimezone(UTC)


def select_as_of(facts: list[Fact], cutoff: datetime) -> tuple[list[Fact], list[str]]:
    candidates: dict[tuple[object, ...], list[Fact]] = defaultdict(list)
    for fact in facts:
        if (
            fact.available(cutoff)
            and fact.period_end <= cutoff.astimezone(ZoneInfo("America/New_York")).date()
        ):
            key = (
                fact.taxonomy,
                fact.tag,
                fact.period_start,
                fact.period_end,
                fact.unit,
                fact.dimensions,
            )
            candidates[key].append(fact)
    selected, issues = [], []
    for rows in candidates.values():
        latest = max(_publication_order(row) for row in rows)
        current = [row for row in rows if _publication_order(row) == latest]
        if len({(row.value, row.value_text if row.value is None else "") for row in current}) > 1:
            issues.append("ambiguous_same_publication_fact")
            continue
        selected.append(
            sorted(current, key=lambda row: (row.accession, row.raw_sha256, row.context_id))[-1]
        )
    return selected, sorted(set(issues))


def _measure(fact: Fact | None) -> Measure:
    if fact is None or fact.value is None:
        return Measure(reason="missing_reported_fact")
    return Measure(value=fact.value, lineage=(_reference(fact),))


def _combine(left: Measure, right: Measure, *, subtract: bool = False) -> Measure:
    if left.value is None or right.value is None:
        return Measure(
            reason=left.reason or right.reason or "missing_component",
            lineage=left.lineage + right.lineage,
        )
    return Measure(
        value=left.value - right.value if subtract else left.value + right.value,
        lineage=left.lineage + right.lineage,
    )


def ratio(numerator: Measure, denominator: Measure, *, growth: bool = False) -> Measure:
    lineage = numerator.lineage + denominator.lineage
    if numerator.value is None or denominator.value is None:
        return Measure(
            reason=numerator.reason or denominator.reason or "missing_component", lineage=lineage
        )
    if denominator.value <= 0:
        return Measure(
            reason="negative_base" if growth else "nonpositive_denominator", lineage=lineage
        )
    result = numerator.value / denominator.value - (Decimal(1) if growth else Decimal(0))
    return Measure(value=result, lineage=lineage)


def quarters(duration: dict[tuple[date, date], Measure]) -> list[Quarter]:
    """Prefer direct quarters; subtract only same-start YTD periods already known as-of."""
    by_end: dict[date, list[Quarter]] = defaultdict(list)
    for (start, end), value in duration.items():
        days = (end - start).days + 1
        if 70 <= days <= 105:
            by_end[end].append(Quarter(start=start, end=end, measure=value))
            continue
        if not 140 <= days <= 390:
            continue
        previous = [
            (prior_end, measure)
            for (prior_start, prior_end), measure in duration.items()
            if prior_start == start and 70 <= (end - prior_end).days <= 105
        ]
        if previous:
            prior_end, prior_value = max(previous, key=lambda pair: pair[0])
            by_end[end].append(
                Quarter(
                    start=prior_end + timedelta(days=1),
                    end=end,
                    measure=_combine(value, prior_value, subtract=True),
                )
            )
    result = []
    for _end, candidates in sorted(by_end.items()):
        starts = {quarter.start for quarter in candidates}
        values = {
            quarter.measure.value for quarter in candidates if quarter.measure.value is not None
        }
        if len(starts) != 1 or len(values) > 1:
            chosen = candidates[0]
            result.append(
                Quarter(
                    start=chosen.start,
                    end=chosen.end,
                    measure=Measure(reason="quarter_reconciliation_mismatch"),
                )
            )
        else:
            # A direct observation has fewer source components than a YTD subtraction.
            result.append(min(candidates, key=lambda quarter: len(quarter.measure.lineage)))
    return result


def _ttm(values: list[Quarter], end: date, *, lag: int = 0) -> tuple[Measure, date | None]:
    available = [quarter for quarter in values if quarter.end <= end]
    if not available or available[-1].end != end or len(available) < lag + 4:
        return Measure(reason="insufficient_contiguous_quarters"), None
    window = available[-(lag + 4) :]
    selected = window[:4]
    if any(
        right.start != left.end + timedelta(days=1)
        for left, right in zip(window, window[1:], strict=False)
    ):
        return Measure(reason="noncontiguous_quarters"), None
    value = Measure(value=Decimal(0))
    for quarter in selected:
        value = _combine(value, quarter.measure)
    return value, selected[0].start


def compute_snapshot(
    facts: list[Fact],
    cutoff: datetime,
    *,
    market_cap: Measure | None = None,
    evidence: AccountingEvidence | None = None,
) -> RatioSnapshot:
    evidence = evidence or AccountingEvidence()
    selected, issues = select_as_of(facts, cutoff)
    consolidated = [
        fact
        for fact in selected
        if not fact.dimensions and fact.taxonomy == "us-gaap" and fact.unit == "USD"
    ]
    assets = [fact for fact in consolidated if fact.tag == "Assets" and fact.period_start is None]
    end = max((fact.period_end for fact in assets), default=None)
    report_dates = {
        fact.document_period_end
        for fact in facts
        if fact.available(cutoff) and fact.document_period_end is not None
    }
    if end is None:
        return RatioSnapshot(
            ratios={name: Measure(reason="no_assets_period") for name in RATIO_AXES},
            period_end=None,
            valid_axes=0,
            reports_available=len(report_dates),
            issues=tuple(issues),
        )

    def get(tag: str, period_end: date, start: date | None = None) -> Measure:
        matches = [
            fact
            for fact in consolidated
            if fact.tag == tag and fact.period_end == period_end and fact.period_start == start
        ]
        if matches:
            return _measure(matches[0])
        return Measure(reason=f"missing:{tag}")

    def equity(period_end: date) -> Measure:
        value = get("StockholdersEquity", period_end)
        preferred = get("PreferredStockValue", period_end)
        if (
            preferred.value is None
            and evidence.no_preferred
            and evidence.references
            and period_end in evidence.no_preferred_period_ends
        ):
            preferred = Measure(value=Decimal(0), lineage=evidence.references)
        return _combine(value, preferred, subtract=True)

    durations = {
        (fact.period_start, fact.period_end)
        for fact in consolidated
        if fact.period_start is not None
    }
    revenues: dict[tuple[date, date], Measure] = {}
    incomes: dict[tuple[date, date], Measure] = {}
    for start, stop in durations:
        if start is None:
            continue
        for tag in REVENUE_TAGS:
            value = get(tag, stop, start)
            if value.value is not None:
                revenues[start, stop] = value
                break
        ni = get(COMMON_NI, stop, start)
        if ni.value is None:
            total_ni = get("NetIncomeLoss", stop, start)
            preferred_dividends = get("PreferredStockDividendsAndOtherAdjustments", stop, start)
            if (
                preferred_dividends.value is None
                and evidence.no_preferred
                and evidence.references
                and stop in evidence.no_preferred_period_ends
            ):
                preferred_dividends = Measure(value=Decimal(0), lineage=evidence.references)
            ni = _combine(total_ni, preferred_dividends, subtract=True)
        if ni.value is not None:
            incomes[start, stop] = ni
    revenue_quarters, income_quarters = quarters(revenues), quarters(incomes)
    if any(
        quarter.measure.reason == "quarter_reconciliation_mismatch"
        for quarter in (*revenue_quarters, *income_quarters)
    ):
        issues.append("quarter_reconciliation_mismatch")
    revenue, _ = _ttm(revenue_quarters, end)
    revenue_lag, _ = _ttm(revenue_quarters, end, lag=4)
    ni, ttm_start = _ttm(income_quarters, end)
    ni_lag, _ = _ttm(income_quarters, end, lag=4)
    asset = get("Assets", end)
    common_equity = equity(end)
    beginning = ttm_start - timedelta(days=1) if ttm_start else end
    average_assets = _combine(asset, get("Assets", beginning))
    average_equity = _combine(common_equity, equity(beginning))
    if average_assets.value is not None:
        average_assets = average_assets.model_copy(update={"value": average_assets.value / 2})
    if average_equity.value is not None:
        average_equity = average_equity.model_copy(update={"value": average_equity.value / 2})
    debt = Measure(value=Decimal(0))
    for tag in ("LongTermDebtCurrent", "LongTermDebtNoncurrent", "ShortTermBorrowings"):
        debt = _combine(debt, get(tag, end))
    if not evidence.debt_nonoverlap_verified or not evidence.references:
        debt = Measure(reason="debt_components_scope_unverified", lineage=debt.lineage)
    cap = market_cap or Measure(reason="common_class_market_cap_unverified")
    values = {
        "roa": ratio(ni, average_assets),
        "roe": ratio(ni, average_equity),
        "revenue_growth": ratio(revenue, revenue_lag, growth=True),
        "earnings_growth": ratio(ni, ni_lag, growth=True),
        "equity_ratio": ratio(common_equity, asset),
        "debt_ratio": ratio(debt, asset),
        "earnings_yield": ratio(ni, cap),
        "book_yield": ratio(common_equity, cap),
    }
    period_age = (cutoff.astimezone(ZoneInfo("America/New_York")).date() - end).days
    latest_stock = max((fact for fact in assets if fact.period_end == end), key=_publication_order)
    published = _publication_order(latest_stock).astimezone(ZoneInfo("America/New_York"))
    cutoff_local = cutoff.astimezone(ZoneInfo("America/New_York"))
    age_quarters = (
        (cutoff_local.year - published.year) * 4
        + (cutoff_local.month - 1) // 3
        - (published.month - 1) // 3
    )
    if period_age < 0 or period_age > 270 or age_quarters > 2:
        values = {
            name: Measure(reason="stale", lineage=value.lineage) for name, value in values.items()
        }
    axis_coverage = {
        axis: sum(
            value.value is not None for name, value in values.items() if RATIO_AXES[name] == axis
        )
        for axis in set(RATIO_AXES.values())
    }
    return RatioSnapshot(
        ratios=values,
        period_end=end,
        valid_axes=sum(count >= 1 for count in axis_coverage.values()),
        axis_coverage=axis_coverage,
        reports_available=len(report_dates),
        issues=tuple(issues),
    )
