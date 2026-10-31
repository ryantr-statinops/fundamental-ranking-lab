"""Data contracts and schemas for portfolio construction and backtest accounting."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

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
