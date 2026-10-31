"""Unit tests for ranking data contracts and schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pyarrow as pa
import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.ranking_contracts import (
    CANDIDATE_SELECTION_SCHEMA,
    INDUSTRY_RANKING_SCHEMA,
    STOCK_SCORE_SCHEMA,
    CandidateSelection,
    IndustryRanking,
    StockScore,
)


def test_stock_score_validates_and_serializes() -> None:
    score = StockScore(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        entity_id="apple",
        security_id="AAPL",
        industry="Machn",
        group="General",
        quality_score=Decimal("0.85"),
        growth_score=Decimal("0.72"),
        health_score=Decimal("0.60"),
        valuation_score=Decimal("0.45"),
        composite_score=Decimal("0.655"),
        valid_axes=4,
        eligible=True,
    )
    assert score.eligible is True
    assert score.composite_score == Decimal("0.655")
    assert pa.types.is_string(STOCK_SCORE_SCHEMA.field("composite_score").type)

    # Strict model rejects unexpected fields
    with pytest.raises(ValidationError):
        StockScore(
            cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
            entity_id="apple",
            security_id="AAPL",
            industry="Machn",
            group="General",
            unexpected="field",
        )


def test_industry_ranking_contract() -> None:
    ir = IndustryRanking(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        industry="Chips",
        rank=1,
        median_composite=Decimal("0.75"),
        iqr_composite=Decimal("0.12"),
        eligible_count=15,
        total_count=20,
        breadth_above_universe_median=Decimal("0.80"),
    )
    assert ir.rank == 1
    assert ir.eligible_count == 15
    assert pa.types.is_int64(INDUSTRY_RANKING_SCHEMA.field("rank").type)


def test_candidate_selection_contract() -> None:
    cand = CandidateSelection(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        entity_id="microsoft",
        security_id="MSFT",
        rank=1,
        composite_score=Decimal("0.98"),
        industry="Other",
        group="General",
        is_border_tie=False,
        selection_reason="top100_primary",
    )
    assert cand.rank == 1
    assert cand.is_border_tie is False
    assert pa.types.is_boolean(CANDIDATE_SELECTION_SCHEMA.field("is_border_tie").type)
