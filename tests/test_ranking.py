"""Unit tests for percentile ranking and directionality."""

from __future__ import annotations

from decimal import Decimal

from fundamental_ranking_lab.ranking import percentile_rank


def test_percentile_rank_empty_and_single() -> None:
    assert percentile_rank({}) == {}
    assert percentile_rank({"a": None, "b": None}) == {"a": None, "b": None}

    single = percentile_rank({"a": Decimal("100"), "b": None})
    assert single["a"] == Decimal("0.5")
    assert single["b"] is None


def test_percentile_rank_standard_two_and_three() -> None:
    res2 = percentile_rank({"a": Decimal("10"), "b": Decimal("20")})
    assert res2["a"] == Decimal("0.0")
    assert res2["b"] == Decimal("1.0")

    res3 = percentile_rank({"a": Decimal("10"), "b": Decimal("20"), "c": Decimal("30")})
    assert res3["a"] == Decimal("0.0")
    assert res3["b"] == Decimal("0.5")
    assert res3["c"] == Decimal("1.0")


def test_percentile_rank_midrank_ties() -> None:
    # 4 elements: a=10, b=20, c=20, d=30
    # b and c tie for rank 2 and 3 -> midrank = 2.5
    # formula: (2.5 - 1) / (4 - 1) = 1.5 / 3 = 0.5
    res = percentile_rank(
        {
            "a": Decimal("10"),
            "b": Decimal("20"),
            "c": Decimal("20"),
            "d": Decimal("30"),
        }
    )
    assert res["a"] == Decimal("0.0")
    assert res["b"] == Decimal("0.5")
    assert res["c"] == Decimal("0.5")
    assert res["d"] == Decimal("1.0")


def test_percentile_rank_low_is_good_reversal() -> None:
    # debt_ratio: lower is better
    # a=10 (best -> score 1.0), b=30 (worst -> score 0.0)
    res = percentile_rank(
        {
            "a": Decimal("10"),
            "b": Decimal("20"),
            "c": Decimal("30"),
        },
        higher_is_better=False,
    )
    assert res["a"] == Decimal("1.0")
    assert res["b"] == Decimal("0.5")
    assert res["c"] == Decimal("0.0")


def test_compute_axes_and_composite_all_four_axes() -> None:
    from fundamental_ranking_lab.ranking import compute_axes_and_composite

    ratio_scores = {
        "roa": Decimal("0.80"),
        "roe": Decimal("0.90"),
        # quality avg = 0.85
        "revenue_growth": Decimal("0.70"),
        "earnings_growth": Decimal("0.70"),
        # growth avg = 0.70
        "equity_ratio": Decimal("0.60"),
        "debt_ratio": Decimal("0.60"),
        # health avg = 0.60
        "earnings_yield": Decimal("0.40"),
        "book_yield": Decimal("0.50"),
        # valuation avg = 0.45
    }
    axes, composite, valid_count = compute_axes_and_composite(ratio_scores)
    assert valid_count == 4
    assert axes["quality"] == Decimal("0.85")
    assert axes["growth"] == Decimal("0.70")
    assert axes["financial_health"] == Decimal("0.60")
    assert axes["valuation"] == Decimal("0.45")
    # composite = (0.85 + 0.70 + 0.60 + 0.45) / 4 = 2.60 / 4 = 0.65
    assert composite == Decimal("0.65")


def test_compute_axes_and_composite_three_axes_threshold() -> None:
    from fundamental_ranking_lab.ranking import compute_axes_and_composite

    # valuation is completely missing (both earnings_yield and book_yield None)
    ratio_scores = {
        "roa": Decimal("0.90"),
        "roe": None,  # 1 of 2 valid is sufficient for quality axis
        # quality avg = 0.90
        "revenue_growth": Decimal("0.80"),
        "earnings_growth": Decimal("0.80"),
        # growth avg = 0.80
        "equity_ratio": Decimal("0.70"),
        "debt_ratio": Decimal("0.70"),
        # health avg = 0.70
        "earnings_yield": None,
        "book_yield": None,
        # valuation missing
    }
    axes, composite, valid_count = compute_axes_and_composite(ratio_scores)
    assert valid_count == 3
    assert axes["valuation"] is None
    # composite = (0.90 + 0.80 + 0.70) / 3 = 2.40 / 3 = 0.80
    assert composite == Decimal("0.80")


def test_compute_axes_and_composite_under_three_axes_returns_none() -> None:
    from fundamental_ranking_lab.ranking import compute_axes_and_composite

    # only 2 valid axes -> composite must be None
    ratio_scores = {
        "roa": Decimal("0.90"),
        "roe": Decimal("0.90"),
        "revenue_growth": Decimal("0.80"),
        "earnings_growth": None,
        "equity_ratio": None,
        "debt_ratio": None,
        "earnings_yield": None,
        "book_yield": None,
    }
    axes, composite, valid_count = compute_axes_and_composite(ratio_scores)
    assert valid_count == 2
    assert composite is None
