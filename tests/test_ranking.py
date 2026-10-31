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
