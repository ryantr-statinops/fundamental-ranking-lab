"""Cross-sectional normalization, axis scoring, and ranking baseline."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any


def percentile_rank(
    values: dict[Any, Decimal | None],
    *,
    higher_is_better: bool = True,
) -> dict[Any, Decimal | None]:
    """Compute fractional mid-rank percentile rank in [0.0, 1.0].

    Formula: (midrank - 1) / (n - 1)
    - If n == 1: returns Decimal("0.5")
    - If n == 0: returns empty dict / None
    - If higher_is_better is False (e.g. debt_ratio): reverses rank (1.0 - rank)
    """
    valid = {k: v for k, v in values.items() if v is not None}
    n = len(valid)
    if n == 0:
        return {k: None for k in values}
    if n == 1:
        single_k = next(iter(valid))
        return {k: Decimal("0.5") if k == single_k else None for k in values}

    sorted_items = sorted(valid.items(), key=lambda item: item[1])

    # Group ties
    grouped: dict[Decimal, list[Any]] = defaultdict(list)
    for k, v in sorted_items:
        grouped[v].append(k)

    ranks: dict[Any, Decimal] = {}
    current_index = 1  # 1-based index
    for val in sorted(grouped):
        keys = grouped[val]
        count = len(keys)
        # midrank is average of ranks in the tie group
        midrank = Decimal(current_index + (current_index + count - 1)) / Decimal(2)
        score = (midrank - Decimal(1)) / Decimal(n - 1)
        if not higher_is_better:
            score = Decimal(1) - score
        for k in keys:
            ranks[k] = score
        current_index += count

    return {k: ranks.get(k) for k in values}


RATIO_DIRECTIONS = {
    "roa": True,
    "roe": True,
    "revenue_growth": True,
    "earnings_growth": True,
    "equity_ratio": True,
    "debt_ratio": False,
    "earnings_yield": True,
    "book_yield": True,
}

AXIS_MAPPINGS = {
    "quality": ("roa", "roe"),
    "growth": ("revenue_growth", "earnings_growth"),
    "financial_health": ("equity_ratio", "debt_ratio"),
    "valuation": ("earnings_yield", "book_yield"),
}


def compute_axes_and_composite(
    ratio_scores: dict[str, Decimal | None],
) -> tuple[dict[str, Decimal | None], Decimal | None, int]:
    """Compute axis scores and core composite score from normalized ratio scores.

    Returns:
        (axis_scores, composite_score, valid_axes_count)
    - An axis is valid if at least 1 of its 2 ratios is non-None.
    - Composite score is average of valid axes if valid_axes >= 3, else None.
    """
    axis_scores: dict[str, Decimal | None] = {}
    valid_axes_list: list[Decimal] = []

    for axis, ratios in AXIS_MAPPINGS.items():
        scores: list[Decimal] = [val for r in ratios if (val := ratio_scores.get(r)) is not None]
        if scores:
            axis_avg = sum(scores, Decimal(0)) / Decimal(len(scores))
            axis_scores[axis] = axis_avg
            valid_axes_list.append(axis_avg)
        else:
            axis_scores[axis] = None
    valid_axes_count = len(valid_axes_list)
    if valid_axes_count >= 3:
        composite = sum(valid_axes_list, Decimal(0)) / Decimal(valid_axes_count)
    else:
        composite = None

    return axis_scores, composite, valid_axes_count
