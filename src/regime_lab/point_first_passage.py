"""First-passage resolution on a timestamped point-price observation stream.

This module does not infer unobserved intrainterval extrema. If a target/stop
was touched between point observations but no supplied observation records it,
the resolver intentionally returns no observed crossing.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PointPassageResult:
    outcome: str
    trigger_time: pd.Timestamp | None
    trigger_price: float | None
    observed_points: int


def resolve_point_first_passage(
    observations: pd.DataFrame,
    *,
    entry_time: pd.Timestamp,
    end_time: pd.Timestamp,
    entry_price: float,
    direction: int,
    barrier_bps: float,
    time_col: str = "market_time_shanghai",
    price_col: str = "price",
) -> PointPassageResult:
    """Resolve the first *observed* symmetric barrier crossing.

    Multiple rows at the same timestamp are treated as one observation bin. If
    that timestamp contains values on both target and stop sides, the ordering
    is unknowable and the result is conservatively `ambiguous_stop_assumed`.
    """

    if direction not in {-1, 1}:
        raise ValueError("direction must be -1 or +1")
    if barrier_bps <= 0 or entry_price <= 0:
        raise ValueError("barrier_bps and entry_price must be positive")
    if end_time < entry_time:
        raise ValueError("end_time must not precede entry_time")
    if time_col not in observations or price_col not in observations:
        raise ValueError("missing observation time/price columns")

    x = observations.loc[
        observations[time_col].between(entry_time, end_time, inclusive="both"),
        [time_col, price_col],
    ].copy()
    x[price_col] = pd.to_numeric(x[price_col], errors="coerce")
    x = x.dropna(subset=[price_col]).sort_values(time_col, kind="stable")

    b = barrier_bps / 1e4
    if direction > 0:
        target = entry_price * (1.0 + b)
        stop = entry_price * (1.0 - b)
    else:
        target = entry_price * (1.0 - b)
        stop = entry_price * (1.0 + b)

    for t, g in x.groupby(time_col, sort=True):
        lo = float(g[price_col].min())
        hi = float(g[price_col].max())
        if direction > 0:
            target_hit = hi >= target
            stop_hit = lo <= stop
            target_price = hi
            stop_price = lo
        else:
            target_hit = lo <= target
            stop_hit = hi >= stop
            target_price = lo
            stop_price = hi

        if target_hit and stop_hit:
            return PointPassageResult(
                "ambiguous_stop_assumed", pd.Timestamp(t), stop_price, int(len(x))
            )
        if target_hit:
            return PointPassageResult("target_first", pd.Timestamp(t), target_price, int(len(x)))
        if stop_hit:
            return PointPassageResult("stop_first", pd.Timestamp(t), stop_price, int(len(x)))

    return PointPassageResult("no_observed_cross", None, None, int(len(x)))
