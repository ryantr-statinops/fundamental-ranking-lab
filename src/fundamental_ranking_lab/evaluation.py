"""Hypothesis testing, Fama-MacBeth regressions, tercile spreads, and statistical inference."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal


def compute_forward_returns(
    prices: dict[tuple[str, datetime], Decimal],
    cutoffs: list[datetime],
) -> dict[tuple[str, datetime], Decimal]:
    """Compute open-to-open forward gross returns between consecutive cutoffs:

    R_{i, t+1} = (Price_{i, t+1} / Price_{i, t}) - 1

    Returns:
        dict mapping (security_id, cutoff_t) -> forward_return
    """
    sorted_cutoffs = sorted(cutoffs)
    returns: dict[tuple[str, datetime], Decimal] = {}

    for idx in range(len(sorted_cutoffs) - 1):
        t_curr = sorted_cutoffs[idx]
        t_next = sorted_cutoffs[idx + 1]

        curr_secs = {sec for sec, t in prices if t == t_curr}
        for sec in curr_secs:
            p_curr = prices.get((sec, t_curr))
            p_next = prices.get((sec, t_next))

            if p_curr is not None and p_next is not None and p_curr > 0:
                ret = (p_next / p_curr) - Decimal(1)
                returns[(sec, t_curr)] = ret

    return returns
