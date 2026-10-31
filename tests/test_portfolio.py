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


def test_water_filling_scenario_1_four_industries_25_stocks_each() -> None:
    # Acceptance scenario from spec:
    # 4 industries, each has 25 stocks with equal raw_a.
    # Total stocks = 100.
    # Each industry cap is 20%, so each industry gets 20% NAV.
    # Total stocks weight = 4 * 20% = 80%.
    # Remaining residual cash = 20%.
    from fundamental_ranking_lab.portfolio import apply_water_filling_caps

    items = []
    for ind in ["Ind1", "Ind2", "Ind3", "Ind4"]:
        for i in range(25):
            items.append(
                {
                    "entity_id": f"{ind}_{i}",
                    "security_id": f"{ind}_{i}",
                    "industry": ind,
                    "raw_a": Decimal("1.0"),
                }
            )
    allocated, cash = apply_water_filling_caps(items)
    total_stock_weight = sum(item["target_weight"] for item in allocated)
    assert round(total_stock_weight, 6) == Decimal("0.800000")
    assert round(cash, 6) == Decimal("0.200000")
    # Each stock gets 20% / 25 = 0.8%
    for item in allocated:
        assert round(item["target_weight"], 6) == Decimal("0.008000")
        assert item["cap_binding"] == "sector_20pct"


def test_water_filling_scenario_2_three_stocks_different_industries() -> None:
    # Acceptance scenario from spec:
    # Only 3 stocks in 3 industries -> each capped at 5% stock cap.
    # Total stocks weight = 15%.
    # Residual cash = 85%.
    from fundamental_ranking_lab.portfolio import apply_water_filling_caps

    items = [
        {"entity_id": "s1", "security_id": "S1", "industry": "Ind1", "raw_a": Decimal("1.0")},
        {"entity_id": "s2", "security_id": "S2", "industry": "Ind2", "raw_a": Decimal("1.0")},
        {"entity_id": "s3", "security_id": "S3", "industry": "Ind3", "raw_a": Decimal("1.0")},
    ]
    allocated, cash = apply_water_filling_caps(items)
    total_stock_weight = sum(item["target_weight"] for item in allocated)
    assert round(total_stock_weight, 6) == Decimal("0.150000")
    assert round(cash, 6) == Decimal("0.850000")
    for item in allocated:
        assert item["target_weight"] == Decimal("0.05")
        assert item["cap_binding"] == "stock_5pct"


def test_water_filling_scenario_3_five_industries_full_allocation() -> None:
    # 5 industries, each with 20 stocks with equal raw_a.
    # 5 * 20% = 100% allocation -> cash = 0%.
    from fundamental_ranking_lab.portfolio import apply_water_filling_caps

    items = []
    for ind in ["Ind1", "Ind2", "Ind3", "Ind4", "Ind5"]:
        for i in range(20):
            items.append(
                {
                    "entity_id": f"{ind}_{i}",
                    "security_id": f"{ind}_{i}",
                    "industry": ind,
                    "raw_a": Decimal("1.0"),
                }
            )
    allocated, cash = apply_water_filling_caps(items)
    total_stock_weight = sum(item["target_weight"] for item in allocated)
    assert round(total_stock_weight, 6) == Decimal("1.000000")
    assert round(cash, 6) == Decimal("0.000000")
    for item in allocated:
        assert round(item["target_weight"], 6) == Decimal("0.010000")


def test_solve_self_financing_execution_initial_entry() -> None:
    # Starting portfolio from all cash (V_minus = 1,000,000, holdings = 0)
    # Target: 50% in stock A, 50% in stock B
    # Fee: 10 bps (0.001)
    # V+ = V- - 0.001 * (0.5*V+ + 0.5*V+) = V- - 0.001 * V+
    # V+ * 1.001 = 1,000,000 -> V+ = 1,000,000 / 1.001 = 999,000.999...
    # Fee = 1,000,000 - V+ = 999.000999...
    from fundamental_ranking_lab.portfolio import solve_self_financing_execution

    v_minus = Decimal("1000000.00")
    target_weights = {"A": Decimal("0.5"), "B": Decimal("0.5")}
    current_holdings = {"A": Decimal("0"), "B": Decimal("0")}

    v_plus, fee, new_holdings, cash_after = solve_self_financing_execution(
        v_minus, current_holdings, target_weights, fee_rate=Decimal("0.001")
    )
    # Exact self-financing balance: V+ + fee == V-
    assert round(v_plus + fee, 4) == v_minus
    assert round(fee, 2) == Decimal("999.00")
    assert round(v_plus, 2) == Decimal("999001.00")
    assert round(cash_after, 4) == Decimal("0.0000")
    assert round(new_holdings["A"] + new_holdings["B"], 2) == round(v_plus, 2)


def test_solve_self_financing_execution_no_trade_zero_fee() -> None:
    # When target holdings match current holdings exactly -> fee must be 0
    from fundamental_ranking_lab.portfolio import solve_self_financing_execution

    v_minus = Decimal("1000000.00")
    target_weights = {"A": Decimal("0.5"), "B": Decimal("0.3")}
    current_holdings = {"A": Decimal("500000.00"), "B": Decimal("300000.00")}

    v_plus, fee, new_holdings, cash_after = solve_self_financing_execution(
        v_minus, current_holdings, target_weights, fee_rate=Decimal("0.001")
    )
    assert fee == Decimal("0")
    assert v_plus == v_minus
    assert cash_after == Decimal("200000.00")
