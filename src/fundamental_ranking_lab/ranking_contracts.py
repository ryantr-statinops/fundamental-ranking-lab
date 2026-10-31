"""Data contracts and schemas for cross-sectional ranking and candidate selection."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

import pyarrow as pa

from fundamental_ranking_lab.config import StrictModel


class StockScore(StrictModel):
    cutoff: datetime
    entity_id: str
    security_id: str
    industry: str
    group: str
    quality_score: Decimal | None = None
    growth_score: Decimal | None = None
    health_score: Decimal | None = None
    valuation_score: Decimal | None = None
    composite_score: Decimal | None = None
    valid_axes: int = 0
    eligible: bool = False
    missing_reason: str | None = None


class IndustryRanking(StrictModel):
    cutoff: datetime
    industry: str
    rank: int
    median_composite: Decimal | None = None
    iqr_composite: Decimal | None = None
    eligible_count: int = 0
    total_count: int = 0
    breadth_above_universe_median: Decimal | None = None


class CandidateSelection(StrictModel):
    cutoff: datetime
    entity_id: str
    security_id: str
    rank: int
    composite_score: Decimal
    industry: str
    group: str
    is_border_tie: bool = False
    selection_reason: Literal["top100_primary", "top100_border_tie", "under_threshold_all"] = (
        "top100_primary"
    )


STOCK_SCORE_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("entity_id", pa.string()),
        ("security_id", pa.string()),
        ("industry", pa.string()),
        ("group", pa.string()),
        ("quality_score", pa.string()),
        ("growth_score", pa.string()),
        ("health_score", pa.string()),
        ("valuation_score", pa.string()),
        ("composite_score", pa.string()),
        ("valid_axes", pa.int64()),
        ("eligible", pa.bool_()),
        ("missing_reason", pa.string()),
    ]
)

INDUSTRY_RANKING_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("industry", pa.string()),
        ("rank", pa.int64()),
        ("median_composite", pa.string()),
        ("iqr_composite", pa.string()),
        ("eligible_count", pa.int64()),
        ("total_count", pa.int64()),
        ("breadth_above_universe_median", pa.string()),
    ]
)

CANDIDATE_SELECTION_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("entity_id", pa.string()),
        ("security_id", pa.string()),
        ("rank", pa.int64()),
        ("composite_score", pa.string()),
        ("industry", pa.string()),
        ("group", pa.string()),
        ("is_border_tie", pa.bool_()),
        ("selection_reason", pa.string()),
    ]
)
