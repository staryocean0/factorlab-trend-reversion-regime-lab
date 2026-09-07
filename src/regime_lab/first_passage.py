"""Conservative first-passage diagnostics for reversal / mean-reversion research.

The signal is formed on completed bar t. Entry is no earlier than the next bar
open. Symmetric target/stop barriers are then inspected using future OHLC bars.
If both barriers are touched inside the same bar, ordering is unknowable from
OHLC and the observation is explicitly marked ambiguous rather than assigning a
favourable fill. Cross-session horizons are rejected.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def symmetric_first_passage(
    frame: pd.DataFrame,
    signal: pd.Series,
    *,
    barrier_bps: float,
    horizon_bars: int,
) -> pd.DataFrame:
    """Measure whether a symmetric target or stop is reached first.

    Parameters
    ----------
    frame:
        Ordered OHLC bars with ``trading_day``. The row at index t is the
        completed signal bar.
    signal:
        +1 for long, -1 for short, 0 otherwise. Entry occurs at open[t+1].
    barrier_bps:
        Symmetric distance from entry in basis points.
    horizon_bars:
        Maximum number of post-signal bars inspected. A signal is valid only
        when the full horizon remains in the same trading day.

    Returns
    -------
    DataFrame with ``valid``, ``entry_price``, ``outcome`` and
    ``resolution_bars``. Outcomes are ``target_first``, ``stop_first``,
    ``ambiguous_same_bar`` or ``neither``.
    """

    if len(frame) != len(signal):
        raise ValueError("frame and signal length mismatch")
    if barrier_bps <= 0:
        raise ValueError("barrier_bps must be positive")
    if horizon_bars < 1:
        raise ValueError("horizon_bars must be >= 1")

    required = {"trading_day", "open", "high", "low"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required columns: {sorted(missing)}")

    direction = pd.to_numeric(signal, errors="coerce").fillna(0).astype(int)
    if not direction.isin({-1, 0, 1}).all():
        raise ValueError("signal must contain only -1, 0, 1")

    open_ = pd.to_numeric(frame["open"], errors="coerce").astype(float)
    high = pd.to_numeric(frame["high"], errors="coerce").astype(float)
    low = pd.to_numeric(frame["low"], errors="coerce").astype(float)
    day = frame["trading_day"].astype(str)

    entry = open_.shift(-1)
    b = float(barrier_bps) / 1e4
    full_same_day = day.shift(-1).eq(day) & day.shift(-horizon_bars).eq(day)
    valid = direction.ne(0) & full_same_day & entry.notna() & entry.gt(0)

    outcome = pd.Series(pd.NA, index=frame.index, dtype="string")
    resolution = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    unresolved = valid.copy()

    long = direction.gt(0)
    short = direction.lt(0)
    long_target = entry * (1.0 + b)
    long_stop = entry * (1.0 - b)
    short_target = entry * (1.0 - b)
    short_stop = entry * (1.0 + b)

    for k in range(1, horizon_bars + 1):
        fh = high.shift(-k)
        fl = low.shift(-k)

        target_hit = (
            (long & fh.ge(long_target))
            | (short & fl.le(short_target))
        )
        stop_hit = (
            (long & fl.le(long_stop))
            | (short & fh.ge(short_stop))
        )

        both = unresolved & target_hit & stop_hit
        target_only = unresolved & target_hit & ~stop_hit
        stop_only = unresolved & stop_hit & ~target_hit

        outcome.loc[both] = "ambiguous_same_bar"
        outcome.loc[target_only] = "target_first"
        outcome.loc[stop_only] = "stop_first"
        resolution.loc[both | target_only | stop_only] = k

        unresolved &= ~(both | target_only | stop_only)

    outcome.loc[unresolved] = "neither"

    return pd.DataFrame(
        {
            "valid": valid,
            "entry_price": entry.where(valid),
            "outcome": outcome.where(valid),
            "resolution_bars": resolution.where(valid),
        },
        index=frame.index,
    )


def summarize_first_passage(events: pd.DataFrame) -> pd.DataFrame:
    """Summarize first-passage outcomes without hiding OHLC ambiguity."""

    required = {"outcome", "resolution_bars"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"missing required event columns: {sorted(missing)}")

    n = int(len(events))
    counts = events["outcome"].value_counts(dropna=False)
    target = int(counts.get("target_first", 0))
    stop = int(counts.get("stop_first", 0))
    ambiguous = int(counts.get("ambiguous_same_bar", 0))
    neither = int(counts.get("neither", 0))
    clean = target + stop

    target_bars = pd.to_numeric(
        events.loc[events["outcome"].eq("target_first"), "resolution_bars"],
        errors="coerce",
    ).dropna()
    stop_bars = pd.to_numeric(
        events.loc[events["outcome"].eq("stop_first"), "resolution_bars"],
        errors="coerce",
    ).dropna()

    return pd.DataFrame(
        [
            {
                "events": n,
                "target_first": target,
                "stop_first": stop,
                "ambiguous_same_bar": ambiguous,
                "neither": neither,
                "target_first_rate": target / n if n else np.nan,
                "stop_first_rate": stop / n if n else np.nan,
                "ambiguous_rate": ambiguous / n if n else np.nan,
                "neither_rate": neither / n if n else np.nan,
                "target_share_clean_resolutions": target / clean if clean else np.nan,
                "target_share_ambiguous_as_adverse": (
                    target / (clean + ambiguous) if (clean + ambiguous) else np.nan
                ),
                "median_bars_to_target": float(target_bars.median()) if len(target_bars) else np.nan,
                "median_bars_to_stop": float(stop_bars.median()) if len(stop_bars) else np.nan,
            }
        ]
    )
