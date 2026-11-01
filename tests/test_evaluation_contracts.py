"""Unit tests for evaluation data contracts and schemas."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pyarrow as pa
import pytest
from pydantic import ValidationError

from fundamental_ranking_lab.evaluation_contracts import (
    EXCESS_RETURN_SCHEMA,
    FAMA_MACBETH_SCHEMA,
    HYPOTHESIS_SUMMARY_SCHEMA,
    TERCILE_SPREAD_SCHEMA,
    ExcessReturnRecord,
    FamaMacBethRecord,
    HypothesisSummary,
    TercileSpreadRecord,
)


def test_fama_macbeth_contract_validation() -> None:
    rec = FamaMacBethRecord(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        slope=Decimal("0.042"),
        t_stat=Decimal("2.15"),
        r_squared=Decimal("0.18"),
        n_observations=40,
        n_industries=6,
    )
    assert rec.slope == Decimal("0.042")
    assert pa.types.is_string(FAMA_MACBETH_SCHEMA.field("slope").type)

    with pytest.raises(ValidationError):
        FamaMacBethRecord(
            cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
            slope=Decimal("0.042"),
            n_observations=40,
            n_industries=6,
            unexpected="field",
        )


def test_tercile_spread_contract_validation() -> None:
    rec = TercileSpreadRecord(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        top_tercile_return=Decimal("0.085"),
        bottom_tercile_return=Decimal("0.021"),
        spread=Decimal("0.064"),
        n_top_industries=2,
        n_bottom_industries=2,
    )
    assert rec.spread == Decimal("0.064")
    assert pa.types.is_string(TERCILE_SPREAD_SCHEMA.field("spread").type)


def test_excess_return_contract_validation() -> None:
    rec = ExcessReturnRecord(
        cutoff=datetime(2025, 12, 31, 21, tzinfo=UTC),
        strategy_net_return=Decimal("0.052"),
        baseline_net_return=Decimal("0.031"),
        net_excess_return=Decimal("0.021"),
        turnover=Decimal("0.15"),
        fee_incurred=Decimal("150.00"),
    )
    assert rec.net_excess_return == Decimal("0.021")
    assert pa.types.is_string(EXCESS_RETURN_SCHEMA.field("net_excess_return").type)


def test_hypothesis_summary_contract_validation() -> None:
    sum_q1 = HypothesisSummary(
        hypothesis_id="Q1",
        metric_name="Fama-MacBeth slope",
        sample_periods=12,
        mean_effect=Decimal("0.035"),
        hac_std_error=Decimal("0.012"),
        hac_t_stat=Decimal("2.91"),
        raw_p_value=Decimal("0.003"),
        bh_adjusted_p_value=Decimal("0.009"),
        ci_lower_95=Decimal("0.011"),
        ci_upper_95=Decimal("0.059"),
        decision="reject_h0",
    )
    assert sum_q1.decision == "reject_h0"
    assert pa.types.is_string(HYPOTHESIS_SUMMARY_SCHEMA.field("mean_effect").type)
