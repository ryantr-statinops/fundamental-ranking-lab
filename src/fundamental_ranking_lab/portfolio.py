"""Portfolio construction, industry tilt, water-filling caps, and self-financing accounting."""

from __future__ import annotations

from decimal import Decimal
from typing import Any


def compute_industry_tilts(
    industry_rankings: list[dict[str, Any]],
    tilt_lambda: Decimal = Decimal("0.5"),
) -> dict[str, Decimal]:
    """Compute industry tilt multipliers T_g in [0.5, 1.5] for each eligible industry.

    Formula:
    - K is number of industries with valid rank (eligible stocks).
    - p_g = (K - rank) / (K - 1) if K > 1 else Decimal("0.5")
    - T_g = 1 + tilt_lambda * (2 * p_g - 1)
    """
    valid_ranks = [r for r in industry_rankings if r.get("median_composite") is not None]
    k = len(valid_ranks)
    if k == 0:
        return {}
    if k == 1:
        return {valid_ranks[0]["industry"]: Decimal("1.0")}

    tilts: dict[str, Decimal] = {}
    for r in valid_ranks:
        ind = r["industry"]
        rank = r["rank"]
        # rank 1 is highest median (p_g = 1.0)
        p_g = Decimal(k - rank) / Decimal(k - 1)
        tilt = Decimal(1) + tilt_lambda * (Decimal(2) * p_g - Decimal(1))
        tilts[ind] = tilt

    return tilts


def compute_raw_weights(
    candidates: list[dict[str, Any]],
    industry_tilts: dict[str, Decimal],
) -> list[dict[str, Any]]:
    """Compute raw weights a_i = s_i * T_g and normalized weights sum to 1.0.

    - Candidates are selected top-100 stocks from Stage 04.
    - If all a_i == 0 or candidates empty: returns weights with target_weight = 0.
    """
    if not candidates:
        return []

    items = []
    total_raw = Decimal(0)
    for cand in candidates:
        score = Decimal(str(cand["composite_score"]))
        ind = cand["industry"]
        tilt = industry_tilts.get(ind, Decimal("1.0"))
        raw_a = score * tilt
        total_raw += raw_a
        items.append(
            {
                **cand,
                "raw_score": score,
                "industry_tilt": tilt,
                "raw_a": raw_a,
            }
        )

    for item in items:
        if total_raw > 0:
            item["raw_weight"] = item["raw_a"] / total_raw
        else:
            item["raw_weight"] = Decimal(0)

    return items


def apply_water_filling_caps(
    items: list[dict[str, Any]],
    stock_cap: Decimal = Decimal("0.05"),
    sector_cap: Decimal = Decimal("0.20"),
    tolerance: Decimal = Decimal("1e-10"),
) -> tuple[list[dict[str, Any]], Decimal]:
    """Apply water-filling allocation algorithm with stock cap (5%) and sector cap (20%).

    Returns:
        (allocated_items, residual_cash_weight)
    - Sum of allocated target_weights + residual_cash_weight == Decimal("1.0").
    - Never renormalizes stocks to 100% after caps are reached.
    """
    if not items:
        return [], Decimal("1.0")

    # Initialize
    n = len(items)
    t: dict[int, Decimal] = {i: Decimal(0) for i in range(n)}
    cap_binding: dict[int, str] = {i: "none" for i in range(n)}
    r = Decimal("1.0")  # Remaining investable capacity

    # Map stocks to industries
    industries = [item["industry"] for item in items]
    unique_industries = set(industries)

    raw_a = [Decimal(str(item.get("raw_a", 0))) for item in items]

    while r > tolerance:
        # Active set: stocks with raw_a > 0 that haven't hit stock_cap
        # and whose industry has not hit sector_cap
        active = []
        for i in range(n):
            if raw_a[i] <= 0:
                continue
            if t[i] >= stock_cap - tolerance:
                continue
            ind = industries[i]
            current_sec_total = sum(t[j] for j in range(n) if industries[j] == ind)
            if current_sec_total >= sector_cap - tolerance:
                continue
            active.append(i)

        if not active:
            break

        sum_active_a = sum(raw_a[i] for i in active)
        if sum_active_a <= 0:
            break

        # Direction d_i for active stocks
        d = {i: raw_a[i] / sum_active_a for i in active}

        # Find maximum step delta before any stock or sector hits cap, or r is exhausted
        limits: list[tuple[Decimal, str, int | str]] = [(r, "capacity", "R")]

        for i in active:
            stock_room = stock_cap - t[i]
            if d[i] > 0:
                limits.append((stock_room / d[i], "stock", i))

        for ind in unique_industries:
            active_in_sec = [i for i in active if industries[i] == ind]
            if active_in_sec:
                sum_d_sec = sum(d[i] for i in active_in_sec)
                current_sec_total = sum(t[j] for j in range(n) if industries[j] == ind)
                sec_room = sector_cap - current_sec_total
                if sum_d_sec > 0:
                    limits.append((sec_room / sum_d_sec, "sector", ind))

        step_delta, limit_type, limit_target = min(limits, key=lambda x: x[0])
        if step_delta <= tolerance:
            # Break if progress is below numerical tolerance
            break

        # Allocate
        for i in active:
            t[i] += step_delta * d[i]
        r -= step_delta

        if limit_type == "stock":
            cap_binding[int(limit_target)] = "stock_5pct"
        elif limit_type == "sector":
            for j in range(n):
                if industries[j] == limit_target and t[j] < stock_cap - tolerance:
                    cap_binding[j] = "sector_20pct"

    results = []
    for i, item in enumerate(items):
        tw = t[i]
        cb = cap_binding[i]
        if tw >= stock_cap - tolerance:
            cb = "stock_5pct"
        results.append(
            {
                **item,
                "target_weight": tw,
                "cap_binding": cb,
            }
        )

    return results, r
