"""Unit tests for portfolio industry tilts and raw weights."""

from __future__ import annotations

from decimal import Decimal

from fundamental_ranking_lab.portfolio import compute_industry_tilts, compute_raw_weights


def test_compute_industry_tilts_three_industries() -> None:
    # 3 industries: Chips (rank 1), Machn (rank 2), Other (rank 3)
    # K = 3
    # Chips: rank 1 -> p_g = (3 - 1) / (3 - 1) = 1.0 -> T_g = 1 + 0.5*(1) = 1.5
    # Machn: rank 2 -> p_g = (3 - 2) / (3 - 1) = 0.5 -> T_g = 1 + 0.5*(0) = 1.0
    # Other: rank 3 -> p_g = (3 - 3) / (3 - 1) = 0.0 -> T_g = 1 + 0.5*(-1) = 0.5
    ranks = [
        {"industry": "Chips", "rank": 1, "median_composite": Decimal("0.80")},
        {"industry": "Machn", "rank": 2, "median_composite": Decimal("0.60")},
        {"industry": "Other", "rank": 3, "median_composite": Decimal("0.40")},
    ]
    tilts = compute_industry_tilts(ranks)
    assert tilts["Chips"] == Decimal("1.5")
    assert tilts["Machn"] == Decimal("1.0")
    assert tilts["Other"] == Decimal("0.5")


def test_compute_industry_tilts_single_industry() -> None:
    ranks = [{"industry": "Chips", "rank": 1, "median_composite": Decimal("0.80")}]
    tilts = compute_industry_tilts(ranks)
    assert tilts["Chips"] == Decimal("1.0")


def test_compute_raw_weights_with_tilts() -> None:
    # 2 candidates:
    # Stock A (Chips, score 0.8) -> a_1 = 0.8 * 1.5 = 1.2
    # Stock B (Other, score 0.8) -> a_2 = 0.8 * 0.5 = 0.4
    # Total raw = 1.6
    # w_A = 1.2 / 1.6 = 0.75
    # w_B = 0.4 / 1.6 = 0.25
    candidates = [
        {
            "entity_id": "a",
            "security_id": "A",
            "industry": "Chips",
            "composite_score": Decimal("0.8"),
        },
        {
            "entity_id": "b",
            "security_id": "B",
            "industry": "Other",
            "composite_score": Decimal("0.8"),
        },
    ]
    tilts = {"Chips": Decimal("1.5"), "Other": Decimal("0.5")}
    items = compute_raw_weights(candidates, tilts)
    assert len(items) == 2
    assert items[0]["raw_a"] == Decimal("1.2")
    assert items[0]["raw_weight"] == Decimal("0.75")
    assert items[1]["raw_a"] == Decimal("0.4")
    assert items[1]["raw_weight"] == Decimal("0.25")
    assert items[0]["raw_weight"] + items[1]["raw_weight"] == Decimal("1.0")
