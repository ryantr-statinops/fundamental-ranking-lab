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
