"""Unit tests for evaluation functions: forward returns and Fama-MacBeth OLS."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from fundamental_ranking_lab.evaluation import (
    compute_forward_returns,
    fama_macbeth_quarterly_ols,
)


def test_compute_forward_returns() -> None:
    t1 = datetime(2025, 3, 31, 21, tzinfo=UTC)
    t2 = datetime(2025, 6, 30, 21, tzinfo=UTC)
    prices = {
        ("AAPL", t1): Decimal("100"),
        ("AAPL", t2): Decimal("110"),  # +10%
        ("MSFT", t1): Decimal("200"),
        ("MSFT", t2): Decimal("180"),  # -10%
    }
    rets = compute_forward_returns(prices, [t1, t2])
    assert rets[("AAPL", t1)] == Decimal("0.10")
    assert rets[("MSFT", t1)] == Decimal("-0.10")


def test_fama_macbeth_quarterly_ols_synthetic() -> None:
    # 6 stocks across 2 industries
    # Return = 0.05 + 0.10 * Score + (0.02 if IndB else 0)
    scores = {
        "s1": Decimal("0.1"),
        "s2": Decimal("0.5"),
        "s3": Decimal("0.9"),
        "s4": Decimal("0.2"),
        "s5": Decimal("0.6"),
        "s6": Decimal("0.8"),
    }
    industries = {
        "s1": "IndA",
        "s2": "IndA",
        "s3": "IndA",
        "s4": "IndB",
        "s5": "IndB",
        "s6": "IndB",
    }
    returns = {
        "s1": Decimal("0.06"),  # 0.05 + 0.01 + 0 = 0.06
        "s2": Decimal("0.10"),  # 0.05 + 0.05 + 0 = 0.10
        "s3": Decimal("0.14"),  # 0.05 + 0.09 + 0 = 0.14
        "s4": Decimal("0.09"),  # 0.05 + 0.02 + 0.02 = 0.09
        "s5": Decimal("0.13"),  # 0.05 + 0.06 + 0.02 = 0.13
        "s6": Decimal("0.15"),  # 0.05 + 0.08 + 0.02 = 0.15
    }
    slope, t_stat, r_sq, n, k = fama_macbeth_quarterly_ols(scores, returns, industries)
    assert slope is not None
    # Slope should be exactly 0.10
    assert round(slope, 2) == Decimal("0.10")
    assert t_stat is not None and t_stat > 10
    assert r_sq is not None and r_sq > Decimal("0.95")
    assert n == 6
    assert k == 2


def test_fama_macbeth_insufficient_observations() -> None:
    # Less than 4 observations
    scores = {"s1": Decimal("0.1"), "s2": Decimal("0.5")}
    returns = {"s1": Decimal("0.05"), "s2": Decimal("0.10")}
    industries = {"s1": "IndA", "s2": "IndA"}
    slope, t_stat, r_sq, n, k = fama_macbeth_quarterly_ols(scores, returns, industries)
    assert slope is None
    assert t_stat is None


def test_compute_industry_tercile_spread() -> None:
    from fundamental_ranking_lab.evaluation import compute_industry_tercile_spread

    # 6 industries with scores 0.1, 0.2, 0.3, 0.4, 0.5, 0.6
    # Returns: Top industries gain 10%, bottom lose -5%
    scores = {
        "Ind1": Decimal("0.10"),
        "Ind2": Decimal("0.20"),
        "Ind3": Decimal("0.30"),
        "Ind4": Decimal("0.40"),
        "Ind5": Decimal("0.50"),
        "Ind6": Decimal("0.60"),
    }
    returns = {
        "Ind1": Decimal("-0.05"),
        "Ind2": Decimal("-0.03"),
        "Ind3": Decimal("0.00"),
        "Ind4": Decimal("0.02"),
        "Ind5": Decimal("0.08"),
        "Ind6": Decimal("0.12"),
    }
    top_ret, bot_ret, spread, n_top, n_bot = compute_industry_tercile_spread(scores, returns)
    assert top_ret is not None and bot_ret is not None and spread is not None
    assert n_top == 2
    assert n_bot == 2
    # Top tercile: Ind5 (0.08) and Ind6 (0.12) -> avg = 0.10
    assert round(top_ret, 2) == Decimal("0.10")
    # Bottom tercile: Ind1 (-0.05) and Ind2 (-0.03) -> avg = -0.04
    assert round(bot_ret, 2) == Decimal("-0.04")
    # Spread = 0.10 - (-0.04) = 0.14
    assert round(spread, 2) == Decimal("0.14")


def test_compute_industry_tercile_spread_under_three_industries() -> None:
    from fundamental_ranking_lab.evaluation import compute_industry_tercile_spread

    # Only 2 industries -> must return None
    scores = {"Ind1": Decimal("0.10"), "Ind2": Decimal("0.50")}
    returns = {"Ind1": Decimal("0.02"), "Ind2": Decimal("0.08")}
    top_ret, bot_ret, spread, n_top, n_bot = compute_industry_tercile_spread(scores, returns)
    assert spread is None
    assert n_top == 0


def test_newey_west_inference_positive_trend() -> None:
    from fundamental_ranking_lab.evaluation import newey_west_inference

    # 10 quarterly excess returns consistently positive (mean around 0.03)
    series = [Decimal(f"0.0{i % 3 + 2}") for i in range(10)]
    mean, hac_se, t_stat, p_val, ci_low, ci_high = newey_west_inference(series)
    assert mean is not None and mean > 0
    assert hac_se is not None and hac_se > 0
    assert t_stat is not None and t_stat > 2.0  # statistically significant
    assert p_val is not None and p_val < Decimal("0.05")
    assert ci_low is not None and ci_high is not None
    assert ci_low < mean < ci_high


def test_newey_west_insufficient_samples() -> None:
    from fundamental_ranking_lab.evaluation import newey_west_inference

    series = [Decimal("0.05"), Decimal("0.02")]
    mean, hac_se, t_stat, p_val, ci_low, ci_high = newey_west_inference(series)
    assert mean == Decimal("0.035")
    assert hac_se is None
    assert p_val is None


def test_benjamini_hochberg_adjust() -> None:
    from fundamental_ranking_lab.evaluation import benjamini_hochberg_adjust

    # 3 p-values for Q1, Q2, Q3:
    # raw = [0.01, 0.04, 0.03]
    # sorted: p(1)=0.01 -> adj = 0.01 * 3 / 1 = 0.03
    #         p(2)=0.03 -> adj = 0.03 * 3 / 2 = 0.045
    #         p(3)=0.04 -> adj = 0.04 * 3 / 3 = 0.04
    # monotonicity backward: p(2) = min(0.045, 0.04) = 0.04
    raw_p = [Decimal("0.01"), Decimal("0.04"), Decimal("0.03")]
    adj_p = benjamini_hochberg_adjust(raw_p)
    assert adj_p[0] == Decimal("0.03")
    assert adj_p[1] == Decimal("0.04")
    assert adj_p[2] == Decimal("0.04")
