"""Second-stage causal confirmations for reversal/MR candidate events."""

from __future__ import annotations

import pandas as pd


def mean_reversion_reentry_signal(
    frame: pd.DataFrame,
    features: pd.DataFrame,
    *,
    stretch_threshold: float = 2.0,
) -> pd.Series:
    """Signal only when an extreme stretch re-enters the same causal band.

    At close ``t-1`` price must be outside +/- ``stretch_threshold``. At close
    ``t`` the stretch must have crossed back inside the band. Signal forms at
    close ``t`` and can enter no earlier than open ``t+1``.

    This is not a threshold search: v0.4 keeps the frozen v0.1 threshold and
    changes only the event geometry from "fade while extreme" to "trade after
    re-entry has actually occurred".
    """

    if stretch_threshold <= 0:
        raise ValueError("stretch_threshold must be positive")
    if len(frame) != len(features):
        raise ValueError("frame and features length mismatch")
    if "trading_day" not in frame.columns:
        raise ValueError("trading_day is required")

    stretch = pd.to_numeric(features["stretch_atr"], errors="coerce")
    prev = stretch.shift(1)
    day = frame["trading_day"].astype(str)
    same_day = day.eq(day.shift(1))

    # Prior downside extreme moves back above the lower boundary -> long.
    long = same_day & prev.le(-stretch_threshold) & stretch.gt(-stretch_threshold)
    # Prior upside extreme moves back below the upper boundary -> short.
    short = same_day & prev.ge(stretch_threshold) & stretch.lt(stretch_threshold)

    signal = pd.Series(0, index=features.index, dtype="int8")
    signal.loc[long] = 1
    signal.loc[short] = -1
    return signal


def structural_reversal_confirmation(
    frame: pd.DataFrame,
    candidate_signal: pd.Series,
) -> pd.Series:
    """Require follow-through through the candidate bar's opposite extreme.

    For a short reversal candidate at close ``t-1``, confirmation at close ``t``
    requires ``C_t < L_{t-1}``. For a long candidate it requires
    ``C_t > H_{t-1}``. The candidate itself is unchanged; this only tests a
    stronger reversal-confirmation geometry. Entry can occur at open ``t+1``.
    """

    if len(frame) != len(candidate_signal):
        raise ValueError("frame and candidate_signal length mismatch")
    required = {"high", "low", "close", "trading_day"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing confirmation columns: {sorted(missing)}")

    high = pd.to_numeric(frame["high"], errors="coerce").astype(float)
    low = pd.to_numeric(frame["low"], errors="coerce").astype(float)
    close = pd.to_numeric(frame["close"], errors="coerce").astype(float)
    candidate = candidate_signal.shift(1).fillna(0).astype("int8")
    day = frame["trading_day"].astype(str)
    same_day = day.eq(day.shift(1))

    long = same_day & candidate.eq(1) & close.gt(high.shift(1))
    short = same_day & candidate.eq(-1) & close.lt(low.shift(1))

    signal = pd.Series(0, index=frame.index, dtype="int8")
    signal.loc[long] = 1
    signal.loc[short] = -1
    return signal
