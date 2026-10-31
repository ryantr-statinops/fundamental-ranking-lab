"""Cross-sectional normalization, axis scoring, and ranking baseline."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
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


def _median_and_iqr(values: list[Decimal]) -> tuple[Decimal | None, Decimal | None]:
    """Compute deterministic median and IQR from sorted Decimal list."""
    if not values:
        return None, None
    s = sorted(values)
    n = len(s)
    mid = n // 2
    median = s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / Decimal(2)

    q1_vals = s[:mid] if n % 2 == 0 else s[:mid]
    q3_vals = s[mid:] if n % 2 == 0 else s[mid + 1 :]

    def _calc_med(lst: list[Decimal]) -> Decimal:
        k = len(lst)
        if k == 0:
            return Decimal(0)
        m = k // 2
        return lst[m] if k % 2 == 1 else (lst[m - 1] + lst[m]) / Decimal(2)

    q1 = _calc_med(q1_vals) if q1_vals else median
    q3 = _calc_med(q3_vals) if q3_vals else median
    iqr = q3 - q1
    return median, iqr


def rank_industries(
    eligible_scores: list[dict[str, Any]],
    cutoff: datetime,
    universe_median_composite: Decimal | None = None,
) -> list[dict[str, Any]]:
    """Rank industries by median composite score of eligible stocks.

    Ties in median are resolved by fractional midrank.
    """
    by_industry: dict[str, list[Decimal]] = defaultdict(list)
    total_counts: dict[str, int] = defaultdict(int)

    for stock in eligible_scores:
        ind = stock["industry"]
        total_counts[ind] += 1
        comp = stock.get("composite_score")
        if comp is not None and stock.get("eligible", False):
            by_industry[ind].append(comp)

    industry_stats = []
    for ind, total in total_counts.items():
        scores = by_industry.get(ind, [])
        median, iqr = _median_and_iqr(scores)
        breadth: Decimal | None = None
        if scores and universe_median_composite is not None:
            above = sum(1 for s in scores if s >= universe_median_composite)
            breadth = Decimal(above) / Decimal(len(scores))

        industry_stats.append(
            {
                "cutoff": cutoff,
                "industry": ind,
                "median_composite": median,
                "iqr_composite": iqr,
                "eligible_count": len(scores),
                "total_count": total,
                "breadth_above_universe_median": breadth,
            }
        )

    # Sort by median descending (None at the end), ties by industry name
    valid_ind = [s for s in industry_stats if s["median_composite"] is not None]
    valid_ind.sort(key=lambda x: (-Decimal(str(x["median_composite"])), str(x["industry"])))

    for rank, item in enumerate(valid_ind, 1):
        item["rank"] = rank

    invalid_ind = [s for s in industry_stats if s["median_composite"] is None]
    for item in invalid_ind:
        item["rank"] = len(valid_ind) + 1

    return valid_ind + invalid_ind


def select_top_candidates(
    eligible_scores: list[dict[str, Any]],
    cutoff: datetime,
    top_k: int = 100,
) -> list[dict[str, Any]]:
    """Select top K candidate stocks by core composite score including border ties.

    - Sort order: descending composite_score, then ascending security_id.
    - If total eligible stocks <= top_k: select all.
    - If stock at index top_k - 1 shares the exact same composite_score with
      subsequent stocks, include all those ties (is_border_tie = True).
    """
    valid_stocks = [
        s
        for s in eligible_scores
        if s.get("eligible", False) and s.get("composite_score") is not None
    ]
    if not valid_stocks:
        return []

    # Sort deterministic: score desc, security_id asc
    valid_stocks.sort(key=lambda s: (-Decimal(str(s["composite_score"])), str(s["security_id"])))

    n = len(valid_stocks)
    if n <= top_k:
        selected = []
        for rank, s in enumerate(valid_stocks, 1):
            selected.append(
                {
                    "cutoff": cutoff,
                    "entity_id": s["entity_id"],
                    "security_id": s["security_id"],
                    "rank": rank,
                    "composite_score": s["composite_score"],
                    "industry": s["industry"],
                    "group": s["group"],
                    "is_border_tie": False,
                    "selection_reason": "under_threshold_all",
                }
            )
        return selected

    threshold_score = Decimal(str(valid_stocks[top_k - 1]["composite_score"]))
    selected = []

    for rank, s in enumerate(valid_stocks, 1):
        score = Decimal(str(s["composite_score"]))
        if rank <= top_k:
            is_tie = (score == threshold_score) and any(
                Decimal(str(valid_stocks[j]["composite_score"])) == threshold_score
                for j in range(top_k, n)
            )
            reason = "top100_border_tie" if is_tie else "top100_primary"
            selected.append(
                {
                    "cutoff": cutoff,
                    "entity_id": s["entity_id"],
                    "security_id": s["security_id"],
                    "rank": rank,
                    "composite_score": s["composite_score"],
                    "industry": s["industry"],
                    "group": s["group"],
                    "is_border_tie": is_tie,
                    "selection_reason": reason,
                }
            )
        elif score == threshold_score:
            # Border tie beyond top_k
            selected.append(
                {
                    "cutoff": cutoff,
                    "entity_id": s["entity_id"],
                    "security_id": s["security_id"],
                    "rank": rank,
                    "composite_score": s["composite_score"],
                    "industry": s["industry"],
                    "group": s["group"],
                    "is_border_tie": True,
                    "selection_reason": "top100_border_tie",
                }
            )
        else:
            break

    return selected
