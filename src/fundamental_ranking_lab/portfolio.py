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

        for i in active:
            if t[i] >= stock_cap - tolerance:
                cap_binding[i] = "stock_5pct"

        for ind in unique_industries:
            current_sec_total = sum(t[j] for j in range(n) if industries[j] == ind)
            if current_sec_total >= sector_cap - tolerance:
                for j in range(n):
                    if industries[j] == ind and cap_binding[j] != "stock_5pct":
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


def solve_self_financing_execution(
    v_minus: Decimal,
    current_holdings: dict[str, Decimal],
    target_weights: dict[str, Decimal],
    fee_rate: Decimal = Decimal("0.001"),  # 10 bps one-way
    tolerance: Decimal = Decimal("1e-10"),
    max_iter: int = 100,
) -> tuple[Decimal, Decimal, dict[str, Decimal], Decimal]:
    """Solve self-financing rebalance equation using bisection:

    V+ = V- - c * sum_i |t_i * V+ - H_i-|

    Returns:
        (v_plus, total_fee, new_holdings, cash_after)
    - Guaranteed: v_plus + total_fee == v_minus within tolerance.
    - All new_holdings and cash_after are >= 0.
    """
    if v_minus <= 0:
        return Decimal(0), Decimal(0), {k: Decimal(0) for k in target_weights}, Decimal(0)

    all_securities = sorted(set(current_holdings.keys()) | set(target_weights.keys()))

    def f(v_p: Decimal) -> tuple[Decimal, Decimal]:
        notional_traded = sum(
            abs(target_weights.get(sec, Decimal(0)) * v_p - current_holdings.get(sec, Decimal(0)))
            for sec in all_securities
        )
        fee = fee_rate * notional_traded
        val = v_p + fee - v_minus
        return val, fee

    # Bisection search interval [low, high]
    low = Decimal(0)
    high = v_minus

    f_low, _ = f(low)
    f_high, _ = f(high)

    if abs(f_high) <= tolerance:
        v_plus = high
        _, fee = f(v_plus)
    else:
        for _ in range(max_iter):
            mid = (low + high) / Decimal(2)
            f_mid, fee_mid = f(mid)
            if abs(f_mid) <= tolerance or (high - low) / v_minus <= tolerance:
                v_plus = mid
                fee = fee_mid
                break
            if f_mid < 0:
                low = mid
            else:
                high = mid
        else:
            v_plus = (low + high) / Decimal(2)
            _, fee = f(v_plus)

    new_holdings = {sec: target_weights.get(sec, Decimal(0)) * v_plus for sec in all_securities}
    total_stock_value = sum(new_holdings.values(), Decimal(0))
    cash_after = v_plus - total_stock_value

    return v_plus, fee, new_holdings, cash_after
