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
