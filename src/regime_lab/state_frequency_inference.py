"""Frozen v1 inference helpers for state-conditioned frequency adaptation.

These functions consume observation rows produced by
``regime_lab.state_frequency_adaptation``. They do not generate states or
change the preregistered horizon/family definitions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import norm

from regime_lab.state_frequency_adaptation import ALLOWED_STATES, COST_GRID_BP, HORIZONS

SHORT_HORIZONS = (1, 2, 3, 5)
LONG_HORIZONS = (10, 15, 30)


def _holm_adjust(p_values: np.ndarray) -> np.ndarray:
    """Holm family-wise p-value adjustment."""
    p = np.asarray(p_values, dtype=float)
    out = np.full_like(p, np.nan)
    valid = np.flatnonzero(np.isfinite(p))
    if not len(valid):
        return out
    order = valid[np.argsort(p[valid], kind="stable")]
    running = 0.0
    m = len(order)
    for rank, idx in enumerate(order):
        adjusted = min(1.0, (m - rank) * p[idx])
        running = max(running, adjusted)
        out[idx] = running
    return out


def seasonality_matched_summary(observations: pd.DataFrame) -> pd.DataFrame:
    """Return fixed-clock matched state curves using equalized stratum mass.

    Within each (year, month, AM/PM, 15-minute bucket) stratum, rows from each
    state are weighted so both states contribute the smaller state count.
    One-state strata are excluded from the matched contrast by construction.
    """
    if observations.empty:
        return pd.DataFrame()

    required = {
        "symbol",
        "trading_day",
        "session_segment",
        "clock_bucket_15m",
        "state",
        "family",
        "horizon_minutes",
        "gross_edge_bp",
        "turnover_units",
    }
    missing = required - set(observations.columns)
    if missing:
        raise ValueError(f"observations missing columns: {sorted(missing)}")

    frame = observations.loc[observations["state"].isin(ALLOWED_STATES)].copy()
    day = pd.to_datetime(frame["trading_day"], errors="raise")
    frame["calendar_year"] = day.dt.year.astype("int64")
    frame["calendar_month"] = day.dt.month.astype("int64")
    frame["_match_weight"] = 0.0
    frame["_matched"] = False

    strata = [
        "symbol",
        "family",
        "horizon_minutes",
        "calendar_year",
        "calendar_month",
        "session_segment",
        "clock_bucket_15m",
    ]
    for _, group in frame.groupby(strata, sort=True):
        counts = group["state"].value_counts()
        if not ALLOWED_STATES.issubset(set(counts.index)):
            continue
        target = float(min(int(counts[state]) for state in ALLOWED_STATES))
        if target <= 0:
            continue
        for state in sorted(ALLOWED_STATES):
            idx = group.index[group["state"].eq(state)]
            frame.loc[idx, "_match_weight"] = target / float(len(idx))
            frame.loc[idx, "_matched"] = True

    frame = frame.loc[frame["_matched"]].copy()
    if frame.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    grouping = ["symbol", "state", "family", "horizon_minutes"]
    for (symbol, state, family, horizon), group in frame.groupby(grouping, sort=True):
        weight = group["_match_weight"].to_numpy(dtype=float)
        gross = group["gross_edge_bp"].to_numpy(dtype=float)
        turnover = group["turnover_units"].to_numpy(dtype=float)
        weight_sum = float(weight.sum())
        weighted_gross_sum = float(np.dot(weight, gross))
        weighted_turnover = float(np.dot(weight, turnover))
        stratum_cols = [
            "calendar_year",
            "calendar_month",
            "session_segment",
            "clock_bucket_15m",
        ]
        row: dict[str, object] = {
            "symbol": symbol,
            "state": state,
            "family": family,
            "horizon_minutes": int(horizon),
            "matched_raw_rows": int(len(group)),
            "matched_effective_weight": weight_sum,
            "matched_strata": int(group[stratum_cols].drop_duplicates().shape[0]),
            "mean_gross_edge_bp": weighted_gross_sum / weight_sum,
            "turnover_units_per_decision": weighted_turnover / weight_sum,
            "break_even_oneway_cost_bp": (
                weighted_gross_sum / weighted_turnover if weighted_turnover > 0 else np.nan
            ),
        }
        for cost in COST_GRID_BP:
            row[f"net_edge_bp_c{int(cost)}"] = (
                weighted_gross_sum - cost * weighted_turnover
            ) / weight_sum
        rows.append(row)

    return pd.DataFrame(rows).sort_values(grouping).reset_index(drop=True)


def frequency_contrasts(curve: pd.DataFrame) -> pd.DataFrame:
    """Compute Unsafe-minus-Recovering break-even curves without family selection."""
    if curve.empty:
        return pd.DataFrame()
    required = {
        "symbol",
        "state",
        "family",
        "horizon_minutes",
        "break_even_oneway_cost_bp",
    }
    missing = required - set(curve.columns)
    if missing:
        raise ValueError(f"curve missing columns: {sorted(missing)}")
    pivot = curve.pivot(
        index=["symbol", "family", "horizon_minutes"],
        columns="state",
        values="break_even_oneway_cost_bp",
    ).reset_index()
    for state in sorted(ALLOWED_STATES):
        if state not in pivot.columns:
            pivot[state] = np.nan
    pivot["delta_break_even_bp"] = pivot["Unsafe"] - pivot["Recovering"]
    denom = pivot["Recovering"]
    pivot["ratio_break_even"] = np.where(
        np.isfinite(denom) & (denom > 1e-12), pivot["Unsafe"] / denom, np.nan
    )
    return pivot.sort_values(["symbol", "family", "horizon_minutes"]).reset_index(drop=True)


def cost_survival_summary(curve: pd.DataFrame) -> pd.DataFrame:
    """Summarize the frozen short/long viability sets at each fixed one-way cost."""
    if curve.empty:
        return pd.DataFrame()
    rows: list[dict[str, object]] = []
    grouping = ["symbol", "state", "family"]
    for (symbol, state, family), group in curve.groupby(grouping, sort=True):
        indexed = group.set_index("horizon_minutes")
        for cost in COST_GRID_BP:
            col = f"net_edge_bp_c{int(cost)}"
            if col not in indexed.columns:
                raise ValueError(f"curve missing column {col}")
            short = indexed.reindex(SHORT_HORIZONS)[col]
            long = indexed.reindex(LONG_HORIZONS)[col]
            rows.append(
                {
                    "symbol": symbol,
                    "state": state,
                    "family": family,
                    "oneway_cost_bp": float(cost),
                    "positive_short_horizons": int(short.gt(0).sum()),
                    "available_short_horizons": int(short.notna().sum()),
                    "equal_weight_short_net_edge_bp": float(short.mean()) if short.notna().any() else np.nan,
                    "positive_long_horizons": int(long.gt(0).sum()),
                    "available_long_horizons": int(long.notna().sum()),
                    "equal_weight_long_net_edge_bp": float(long.mean()) if long.notna().any() else np.nan,
                }
            )
    return pd.DataFrame(rows).sort_values(
        ["symbol", "state", "family", "oneway_cost_bp"]
    ).reset_index(drop=True)


def day_block_break_even_uncertainty(
    observations: pd.DataFrame, *, n_boot: int = 2000, seed: int = 20260908
) -> pd.DataFrame:
    """Day-block bootstrap Delta_B(h) with Holm correction over seven horizons.

    The same resampled day multiplicities are used for all horizons inside an
    (asset, family) family, preserving cross-horizon day dependence.
    """
    if observations.empty:
        return pd.DataFrame()
    if n_boot < 200:
        raise ValueError("n_boot must be at least 200 for the frozen inference harness")

    required = {
        "symbol",
        "trading_day",
        "state",
        "family",
        "horizon_minutes",
        "gross_edge_bp",
        "turnover_units",
    }
    missing = required - set(observations.columns)
    if missing:
        raise ValueError(f"observations missing columns: {sorted(missing)}")

    rng = np.random.default_rng(seed)
    all_rows: list[dict[str, object]] = []

    for (symbol, family), fam in observations.groupby(["symbol", "family"], sort=True):
        days = np.array(sorted(fam["trading_day"].astype(str).unique()), dtype=object)
        if len(days) < 2:
            continue
        day_to_idx = {day: i for i, day in enumerate(days)}
        agg = (
            fam.groupby(["trading_day", "state", "horizon_minutes"], sort=True)
            .agg(
                gross_edge_bp=("gross_edge_bp", "sum"),
                turnover_units=("turnover_units", "sum"),
            )
            .reset_index()
        )

        horizon_list = list(HORIZONS)
        state_list = ["Unsafe", "Recovering"]
        gross = np.zeros((len(horizon_list), 2, len(days)), dtype=float)
        turnover = np.zeros_like(gross)
        h_to_idx = {h: i for i, h in enumerate(horizon_list)}
        s_to_idx = {s: i for i, s in enumerate(state_list)}
        for row in agg.itertuples(index=False):
            if row.state not in s_to_idx or int(row.horizon_minutes) not in h_to_idx:
                continue
            hi = h_to_idx[int(row.horizon_minutes)]
            si = s_to_idx[str(row.state)]
            di = day_to_idx[str(row.trading_day)]
            gross[hi, si, di] += float(row.gross_edge_bp)
            turnover[hi, si, di] += float(row.turnover_units)

        observed = np.full(len(horizon_list), np.nan)
        for hi in range(len(horizon_list)):
            if turnover[hi, 0].sum() > 0 and turnover[hi, 1].sum() > 0:
                observed[hi] = (
                    gross[hi, 0].sum() / turnover[hi, 0].sum()
                    - gross[hi, 1].sum() / turnover[hi, 1].sum()
                )

        boot = np.full((n_boot, len(horizon_list)), np.nan)
        for b in range(n_boot):
            sampled = rng.integers(0, len(days), size=len(days))
            counts = np.bincount(sampled, minlength=len(days)).astype(float)
            for hi in range(len(horizon_list)):
                gu = float(np.dot(gross[hi, 0], counts))
                tu = float(np.dot(turnover[hi, 0], counts))
                gr = float(np.dot(gross[hi, 1], counts))
                tr = float(np.dot(turnover[hi, 1], counts))
                if tu > 0 and tr > 0:
                    boot[b, hi] = gu / tu - gr / tr

        p_raw = np.full(len(horizon_list), np.nan)
        se = np.full(len(horizon_list), np.nan)
        ci_low = np.full(len(horizon_list), np.nan)
        ci_high = np.full(len(horizon_list), np.nan)
        for hi in range(len(horizon_list)):
            vals = boot[:, hi]
            vals = vals[np.isfinite(vals)]
            if len(vals) < max(100, n_boot // 2) or not np.isfinite(observed[hi]):
                continue
            se[hi] = float(np.std(vals, ddof=1))
            ci_low[hi], ci_high[hi] = np.quantile(vals, [0.025, 0.975])
            if se[hi] == 0:
                p_raw[hi] = 0.0 if observed[hi] != 0 else 1.0
            else:
                p_raw[hi] = float(2.0 * norm.sf(abs(observed[hi] / se[hi])))

        p_holm = _holm_adjust(p_raw)
        for hi, horizon in enumerate(horizon_list):
            all_rows.append(
                {
                    "symbol": symbol,
                    "family": family,
                    "horizon_minutes": int(horizon),
                    "delta_break_even_bp": observed[hi],
                    "bootstrap_se_bp": se[hi],
                    "ci95_low_bp": ci_low[hi],
                    "ci95_high_bp": ci_high[hi],
                    "p_raw": p_raw[hi],
                    "p_holm_7": p_holm[hi],
                    "positive_after_holm_5pct": bool(
                        np.isfinite(observed[hi])
                        and observed[hi] > 0
                        and np.isfinite(p_holm[hi])
                        and p_holm[hi] < 0.05
                    ),
                    "bootstrap_days": int(len(days)),
                    "n_boot": int(n_boot),
                    "bootstrap_seed": int(seed),
                }
            )

    return pd.DataFrame(all_rows).sort_values(
        ["symbol", "family", "horizon_minutes"]
    ).reset_index(drop=True)
