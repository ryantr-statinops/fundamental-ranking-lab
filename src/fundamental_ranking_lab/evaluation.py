"""Hypothesis testing, Fama-MacBeth regressions, tercile spreads, and statistical inference."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal


def compute_forward_returns(
    prices: dict[tuple[str, datetime], Decimal],
    cutoffs: list[datetime],
) -> dict[tuple[str, datetime], Decimal]:
    """Compute open-to-open forward gross returns between consecutive cutoffs:

    R_{i, t+1} = (Price_{i, t+1} / Price_{i, t}) - 1

    Returns:
        dict mapping (security_id, cutoff_t) -> forward_return
    """
    sorted_cutoffs = sorted(cutoffs)
    returns: dict[tuple[str, datetime], Decimal] = {}

    for idx in range(len(sorted_cutoffs) - 1):
        t_curr = sorted_cutoffs[idx]
        t_next = sorted_cutoffs[idx + 1]

        curr_secs = {sec for sec, t in prices if t == t_curr}
        for sec in curr_secs:
            p_curr = prices.get((sec, t_curr))
            p_next = prices.get((sec, t_next))

            if p_curr is not None and p_next is not None and p_curr > 0:
                ret = (p_next / p_curr) - Decimal(1)
                returns[(sec, t_curr)] = ret

    return returns


def fama_macbeth_quarterly_ols(
    scores: dict[str, Decimal],
    returns: dict[str, Decimal],
    industries: dict[str, str],
) -> tuple[Decimal | None, Decimal | None, Decimal | None, int, int]:
    """Execute cross-sectional OLS for a single quarter:

    Return_i = alpha + beta * Score_i + sum_g gamma_g * IndustryDummy_g + eps_i

    Returns:
        (slope_beta, t_stat, r_squared, n_observations, n_industries)
    - Drops one industry dummy to avoid perfect multicollinearity.
    - Returns None if singular or insufficient degrees of freedom.
    """
    import numpy as np

    # Find common securities with valid score and return
    common_secs = sorted(set(scores.keys()) & set(returns.keys()) & set(industries.keys()))
    n = len(common_secs)
    if n < 4:
        return None, None, None, n, 0

    unique_inds = sorted({industries[sec] for sec in common_secs})
    k_inds = len(unique_inds)
    # Drop the first industry dummy
    dummy_inds = unique_inds[1:]

    # Construct design matrix X: [1.0 (intercept), score, dummy_1, ..., dummy_k-1]
    x_rows = []
    y_vals = []
    for sec in common_secs:
        y_vals.append(float(returns[sec]))
        row = [1.0, float(scores[sec])]
        sec_ind = industries[sec]
        for d_ind in dummy_inds:
            row.append(1.0 if sec_ind == d_ind else 0.0)
        x_rows.append(row)

    X = np.array(x_rows, dtype=np.float64)
    y = np.array(y_vals, dtype=np.float64)

    n_features = X.shape[1]
    if n <= n_features:
        return None, None, None, n, k_inds

    try:
        # OLS beta = (X^T X)^{-1} X^T y
        xtx = X.T @ X
        inv_xtx = np.linalg.inv(xtx)
        betas = inv_xtx @ (X.T @ y)

        # Residuals and standard error
        residuals = y - (X @ betas)
        dof = n - n_features
        sigma_sq = np.sum(residuals**2) / dof
        cov_betas = sigma_sq * inv_xtx

        slope = Decimal(str(round(betas[1], 8)))
        se_slope = np.sqrt(max(1e-12, cov_betas[1, 1]))
        t_stat = Decimal(str(round(betas[1] / se_slope, 4)))

        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_sq = 1.0 - (np.sum(residuals**2) / ss_tot) if ss_tot > 0 else 0.0
        r_squared = Decimal(str(round(max(0.0, r_sq), 4)))

        return slope, t_stat, r_squared, n, k_inds
    except np.linalg.LinAlgError:
        return None, None, None, n, k_inds
