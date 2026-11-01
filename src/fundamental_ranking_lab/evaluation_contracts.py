"""Data contracts and schemas for hypothesis testing, statistical inference, and evaluation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

import pyarrow as pa

from fundamental_ranking_lab.config import StrictModel


class FamaMacBethRecord(StrictModel):
    cutoff: datetime
    slope: Decimal
    t_stat: Decimal | None = None
    r_squared: Decimal | None = None
    n_observations: int
    n_industries: int


class TercileSpreadRecord(StrictModel):
    cutoff: datetime
    top_tercile_return: Decimal
    bottom_tercile_return: Decimal
    spread: Decimal
    n_top_industries: int
    n_bottom_industries: int


class ExcessReturnRecord(StrictModel):
    cutoff: datetime
    strategy_net_return: Decimal
    baseline_net_return: Decimal
    net_excess_return: Decimal
    turnover: Decimal
    fee_incurred: Decimal


class HypothesisSummary(StrictModel):
    hypothesis_id: Literal["Q1", "Q2", "Q3"]
    metric_name: str
    sample_periods: int
    mean_effect: Decimal
    hac_std_error: Decimal | None = None
    hac_t_stat: Decimal | None = None
    raw_p_value: Decimal | None = None
    bh_adjusted_p_value: Decimal | None = None
    ci_lower_95: Decimal | None = None
    ci_upper_95: Decimal | None = None
    decision: Literal["reject_h0", "fail_to_reject_h0", "inconclusive", "insufficient_data"] = (
        "insufficient_data"
    )


FAMA_MACBETH_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("slope", pa.string()),
        ("t_stat", pa.string()),
        ("r_squared", pa.string()),
        ("n_observations", pa.int64()),
        ("n_industries", pa.int64()),
    ]
)

TERCILE_SPREAD_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("top_tercile_return", pa.string()),
        ("bottom_tercile_return", pa.string()),
        ("spread", pa.string()),
        ("n_top_industries", pa.int64()),
        ("n_bottom_industries", pa.int64()),
    ]
)

EXCESS_RETURN_SCHEMA = pa.schema(
    [
        ("cutoff", pa.timestamp("us", tz="UTC")),
        ("strategy_net_return", pa.string()),
        ("baseline_net_return", pa.string()),
        ("net_excess_return", pa.string()),
        ("turnover", pa.string()),
        ("fee_incurred", pa.string()),
    ]
)

HYPOTHESIS_SUMMARY_SCHEMA = pa.schema(
    [
        ("hypothesis_id", pa.string()),
        ("metric_name", pa.string()),
        ("sample_periods", pa.int64()),
        ("mean_effect", pa.string()),
        ("hac_std_error", pa.string()),
        ("hac_t_stat", pa.string()),
        ("raw_p_value", pa.string()),
        ("bh_adjusted_p_value", pa.string()),
        ("ci_lower_95", pa.string()),
        ("ci_upper_95", pa.string()),
        ("decision", pa.string()),
    ]
)
