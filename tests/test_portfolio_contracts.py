"""Unit tests for portfolio contracts and schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pyarrow as pa
import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.portfolio_contracts import (
    PORTFOLIO_HOLDINGS_SCHEMA,
    REBALANCE_RECORD_SCHEMA,
    TARGET_WEIGHTS_SCHEMA,
    PortfolioHolding,
    RebalanceRecord,
    TargetWeight,
)


def test_target_weight_validation() -> None:
    tw = TargetWeight(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        entity_id="apple",
        security_id="AAPL",
        industry="Machn",
        group="General",
        raw_score=Decimal("0.85"),
        industry_tilt=Decimal("1.25"),
        raw_weight=Decimal("0.04"),
        target_weight=Decimal("0.05"),
        cap_binding="stock_5pct",
    )
    assert tw.target_weight == Decimal("0.05")
    assert tw.cap_binding == "stock_5pct"
    assert pa.types.is_string(TARGET_WEIGHTS_SCHEMA.field("target_weight").type)

    with pytest.raises(ValidationError):
        TargetWeight(
            cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
            entity_id="apple",
            security_id="AAPL",
            industry="Machn",
            group="General",
            raw_score=Decimal("0.85"),
            industry_tilt=Decimal("1.25"),
            raw_weight=Decimal("0.04"),
            target_weight=Decimal("0.05"),
            cap_binding="invalid_cap",  # type: ignore[arg-type]
        )


def test_portfolio_holding_validation() -> None:
    h = PortfolioHolding(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        security_id="MSFT",
        shares=Decimal("150.5"),
        price=Decimal("420.00"),
        market_value=Decimal("63210.00"),
        weight=Decimal("0.045"),
    )
    assert h.shares == Decimal("150.5")
    assert pa.types.is_string(PORTFOLIO_HOLDINGS_SCHEMA.field("shares").type)


def test_rebalance_record_validation() -> None:
    rec = RebalanceRecord(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        execution_time=datetime(2026, 1, 2, 14, 30, tzinfo=UTC),
        v_minus=Decimal("1000000.00"),
        v_plus=Decimal("999900.00"),
        fee_incurred=Decimal("100.00"),
        cash_before=Decimal("200000.00"),
        cash_after=Decimal("150000.00"),
        total_stock_weight=Decimal("0.85"),
        cash_weight=Decimal("0.15"),
        turnover=Decimal("0.20"),
    )
    assert rec.fee_incurred == Decimal("100.00")
    assert pa.types.is_string(REBALANCE_RECORD_SCHEMA.field("turnover").type)
