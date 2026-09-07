"""Causal barrier-plus-timeout diagnostics for frozen reversal candidates.

Signal is observed after completed bar t. Entry is the next bar open. Target and
stop are inspected on future OHLC bars. If both are touched in one bar, ordering
is unknowable and the policy conservatively assumes the stop. If neither is
reached by the frozen cap, the policy exits at the cap bar close.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def evaluate_barrier_timeout_policy(
    frame: pd.DataFrame,
    signal: pd.Series,
    *,
    barrier_bps: float,
    horizon_bars: int,
) -> pd.DataFrame:
    """Evaluate symmetric barrier policy with conservative same-bar ambiguity.

    `signal` must contain -1 / 0 / +1. The returned `gross_policy_bps` is a
    diagnostic index return before any spread, fees, slippage, market impact or
    tradable-vehicle basis.
    """

    if len(frame) != len(signal):
        raise ValueError("frame and signal length mismatch")
    if barrier_bps <= 0:
        raise ValueError("barrier_bps must be positive")
    if horizon_bars < 1:
        raise ValueError("horizon_bars must be >= 1")

    required = {"trading_day", "open", "high", "low", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")

    direction = pd.to_numeric(signal, errors="coerce").fillna(0).astype(int)
    if not direction.isin({-1, 0, 1}).all():
        raise ValueError("signal must contain only -1, 0, 1")

    day = frame["trading_day"].astype(str)
    open_ = pd.to_numeric(frame["open"], errors="coerce").astype(float)
    high = pd.to_numeric(frame["high"], errors="coerce").astype(float)
    low = pd.to_numeric(frame["low"], errors="coerce").astype(float)
    close = pd.to_numeric(frame["close"], errors="coerce").astype(float)

    entry = open_.shift(-1)
    b = float(barrier_bps) / 1e4
    full_same_day = day.shift(-1).eq(day) & day.shift(-horizon_bars).eq(day)
    valid = direction.ne(0) & full_same_day & entry.notna() & entry.gt(0)

    long = direction.gt(0)
    short = direction.lt(0)
    long_target = entry * (1.0 + b)
    long_stop = entry * (1.0 - b)
    short_target = entry * (1.0 - b)
    short_stop = entry * (1.0 + b)

    outcome = pd.Series(pd.NA, index=frame.index, dtype="string")
    resolution = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    gross = pd.Series(np.nan, index=frame.index, dtype=float)
    unresolved = valid.copy()

    for k in range(1, horizon_bars + 1):
        fh = high.shift(-k)
        fl = low.shift(-k)
        target_hit = (long & fh.ge(long_target)) | (short & fl.le(short_target))
        stop_hit = (long & fl.le(long_stop)) | (short & fh.ge(short_stop))

        both = unresolved & target_hit & stop_hit
        target_only = unresolved & target_hit & ~stop_hit
        stop_only = unresolved & stop_hit & ~target_hit

        outcome.loc[both] = "ambiguous_stop_assumed"
        outcome.loc[target_only] = "target_first"
        outcome.loc[stop_only] = "stop_first"
        resolution.loc[both | target_only | stop_only] = k
        gross.loc[both | stop_only] = -float(barrier_bps)
        gross.loc[target_only] = float(barrier_bps)

        unresolved &= ~(both | target_only | stop_only)

    timeout_close = close.shift(-horizon_bars)
    timeout_ret_bps = direction.astype(float) * (timeout_close / entry - 1.0) * 1e4
    outcome.loc[unresolved] = "time_out"
    resolution.loc[unresolved] = horizon_bars
    gross.loc[unresolved] = timeout_ret_bps.loc[unresolved]

    return pd.DataFrame(
        {
            "valid": valid,
            "entry_price": entry.where(valid),
            "outcome": outcome.where(valid),
            "resolution_bars": resolution.where(valid),
            "gross_policy_bps": gross.where(valid),
        },
        index=frame.index,
    )


def summarize_barrier_timeout(events: pd.DataFrame) -> pd.DataFrame:
    """Return one-row policy and first-passage summary."""

    required = {"outcome", "resolution_bars", "gross_policy_bps"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"missing required event columns: {sorted(missing)}")

    n = int(len(events))
    counts = events["outcome"].value_counts(dropna=False)
    target = int(counts.get("target_first", 0))
    stop = int(counts.get("stop_first", 0))
    ambiguous = int(counts.get("ambiguous_stop_assumed", 0))
    timeout = int(counts.get("time_out", 0))
    clean = target + stop
    conservative_resolved = target + stop + ambiguous

    pnl = pd.to_numeric(events["gross_policy_bps"], errors="coerce").dropna()
    if len(pnl) >= 20:
        lo, hi = pnl.quantile([0.05, 0.95])
        central = pnl.loc[pnl.between(lo, hi, inclusive="both")]
    else:
        central = pnl

    target_minutes = pd.to_numeric(
        events.loc[events["outcome"].eq("target_first"), "resolution_bars"], errors="coerce"
    ).dropna()
    stop_minutes = pd.to_numeric(
        events.loc[events["outcome"].eq("stop_first"), "resolution_bars"], errors="coerce"
    ).dropna()

    mean_bps = float(pnl.mean()) if len(pnl) else np.nan
    return pd.DataFrame(
        [
            {
                "events": n,
                "target_first": target,
                "stop_first": stop,
                "ambiguous_stop_assumed": ambiguous,
                "time_out": timeout,
                "clean_target_share": target / clean if clean else np.nan,
                "conservative_target_share": target / conservative_resolved if conservative_resolved else np.nan,
                "gross_policy_mean_bps": mean_bps,
                "gross_policy_median_bps": float(pnl.median()) if len(pnl) else np.nan,
                "gross_policy_win_rate": float((pnl > 0).mean()) if len(pnl) else np.nan,
                "central90_mean_bps": float(central.mean()) if len(central) else np.nan,
                "break_even_round_trip_cost_bps": mean_bps,
                "median_minutes_to_target": float(target_minutes.median()) if len(target_minutes) else np.nan,
                "median_minutes_to_stop": float(stop_minutes.median()) if len(stop_minutes) else np.nan,
            }
        ]
    )
