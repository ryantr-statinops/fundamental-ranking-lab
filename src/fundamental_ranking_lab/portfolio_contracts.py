"""Data contracts and schemas for portfolio construction and backtest accounting."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

import pyarrow as pa

from fundamental_ranking_lab.config import StrictModel


class TargetWeight(StrictModel):
    cutoff: datetime
    entity_id: str
    security_id: str
    industry: str
    group: str
    raw_score: Decimal
    industry_tilt: Decimal
    raw_weight: Decimal
    target_weight: Decimal
    cap_binding: Literal["none", "stock_5pct", "sector_20pct"] = "none"


class PortfolioHolding(StrictModel):
    cutoff: datetime
    security_id: str
    shares: Decimal
    price: Decimal
    market_value: Decimal
    weight: Decimal


class RebalanceRecord(StrictModel):
    cutoff: datetime
    execution_time: datetime
    v_minus: Decimal
    v_plus: Decimal
    fee_incurred: Decimal
    cash_before: Decimal
    cash_after: Decimal
    total_stock_weight: Decimal
    cash_weight: Decimal
    turnover: Decimal


TARGET_WEIGHTS_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("entity_id", pa.string()),
        ("security_id", pa.string()),
        ("industry", pa.string()),
        ("group", pa.string()),
        ("raw_score", pa.string()),
        ("industry_tilt", pa.string()),
        ("raw_weight", pa.string()),
        ("target_weight", pa.string()),
        ("cap_binding", pa.string()),
    ]
)

PORTFOLIO_HOLDINGS_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("security_id", pa.string()),
        ("shares", pa.string()),
        ("price", pa.string()),
        ("market_value", pa.string()),
        ("weight", pa.string()),
    ]
)

REBALANCE_RECORD_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("execution_time", pa.timestamp("us", tz="UTC")),
        ("v_minus", pa.string()),
        ("v_plus", pa.string()),
        ("fee_incurred", pa.string()),
        ("cash_before", pa.string()),
        ("cash_after", pa.string()),
        ("total_stock_weight", pa.string()),
        ("cash_weight", pa.string()),
        ("turnover", pa.string()),
    ]
)
