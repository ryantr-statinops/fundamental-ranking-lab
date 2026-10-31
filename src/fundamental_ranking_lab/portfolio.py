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
