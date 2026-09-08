"""Frozen v1 measurement core for state-conditioned frequency adaptation.

This module deliberately does not generate market states.  It consumes a
point-in-time state pool and verified 1-minute market data, then evaluates two
fixed sign-based diagnostic control families on the preregistered horizon grid.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

ALLOWED_STATES = {"Unsafe", "Recovering"}
HORIZONS = (1, 2, 3, 5, 10, 15, 30)
COST_GRID_BP = (1.0, 2.0, 3.0, 5.0)


class StatePoolError(ValueError):
    """Raised when state-pool provenance or point-in-time integrity fails."""


def _as_shanghai(series: pd.Series) -> pd.Series:
    values = pd.to_datetime(series, errors="raise")
    if getattr(values.dt, "tz", None) is None:
        return values.dt.tz_localize("Asia/Shanghai")
    return values.dt.tz_convert("Asia/Shanghai")


def validate_state_pool(state_pool: pd.DataFrame) -> pd.DataFrame:
    """Validate the minimal point-in-time state contract and return a stable copy."""

    required = {"symbol", "market_time_shanghai", "state", "state_available_at"}
    missing = required - set(state_pool.columns)
    if missing:
        raise StatePoolError(f"state pool missing columns: {sorted(missing)}")

    out = state_pool.copy()
    out["market_time_shanghai"] = _as_shanghai(out["market_time_shanghai"])
    out["state_available_at"] = _as_shanghai(out["state_available_at"])

    if out.duplicated(["symbol", "market_time_shanghai"]).any():
        raise StatePoolError("duplicate state rows for symbol/timestamp")
    if (out["state_available_at"] > out["market_time_shanghai"]).any():
        raise StatePoolError("state availability is later than decision timestamp")
    if (out["market_time_shanghai"].dt.year >= 2026).any():
        raise StatePoolError("2026 rows are outside the frozen data role")

    return out.sort_values(["symbol", "market_time_shanghai"], kind="stable").reset_index(drop=True)


def continuous_session_segment(times: pd.Series) -> pd.Series:
    """Map Shanghai wall-clock times to the two continuous-auction segments."""

    minute = times.dt.hour * 60 + times.dt.minute
    out = pd.Series(pd.NA, index=times.index, dtype="string")
    out.loc[minute.between(9 * 60 + 30, 11 * 60 + 30)] = "AM"
    out.loc[minute.between(13 * 60, 15 * 60)] = "PM"
    return out


def session_minute_index(times: pd.Series, segment: pd.Series) -> pd.Series:
    """Return the physical trading-minute index inside each continuous segment."""

    minute = times.dt.hour * 60 + times.dt.minute
    out = pd.Series(np.nan, index=times.index, dtype="float64")
    out.loc[segment.eq("AM")] = minute.loc[segment.eq("AM")] - (9 * 60 + 30)
    out.loc[segment.eq("PM")] = minute.loc[segment.eq("PM")] - (13 * 60)
    return out


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def strict_quality_mask(frame: pd.DataFrame) -> pd.Series:
    """Apply the supplied 1-minute high-frequency quality flags without repair."""

    mask = pd.Series(True, index=frame.index)
    if "high_frequency_analysis_eligible" in frame.columns:
        mask &= _truthy(frame["high_frequency_analysis_eligible"])
    if "causal_flat_fill" in frame.columns:
        mask &= ~_truthy(frame["causal_flat_fill"])
    if "source_minute_count" in frame.columns:
        count = pd.to_numeric(frame["source_minute_count"], errors="coerce")
        mask &= count.ge(1)
    return mask


def build_frequency_observations(
    market: pd.DataFrame,
    state_pool: pd.DataFrame,
    *,
    horizon: int,
    family: str,
) -> pd.DataFrame:
    """Build the frozen non-overlapping state/frequency diagnostic observations."""

    if horizon not in HORIZONS:
        raise ValueError(f"horizon must be one of {HORIZONS}")
    if family not in {"trend", "reversion"}:
        raise ValueError("family must be trend or reversion")

    required = {"symbol", "trading_day", "market_time_shanghai", "close"}
    missing = required - set(market.columns)
    if missing:
        raise ValueError(f"market data missing columns: {sorted(missing)}")

    symbols = set(market["symbol"].dropna().astype(str))
    if len(symbols) != 1:
        raise ValueError("market frame must contain exactly one symbol")
    symbol = next(iter(symbols))

    frame = market.copy()
    frame["market_time_shanghai"] = _as_shanghai(frame["market_time_shanghai"])
    frame = frame.loc[strict_quality_mask(frame)].copy()
    frame["session_segment"] = continuous_session_segment(frame["market_time_shanghai"])
    frame = frame.loc[frame["session_segment"].notna()].copy()
    frame["segment_minute"] = session_minute_index(
        frame["market_time_shanghai"], frame["session_segment"]
    ).astype("int64")
    frame["close"] = pd.to_numeric(frame["close"], errors="raise")

    if (frame["close"] <= 0).any():
        raise ValueError("non-positive close")
    if frame.duplicated(["market_time_shanghai"]).any():
        raise ValueError("duplicate 1m market timestamps")

    states = validate_state_pool(state_pool)
    states = states.loc[states["symbol"].astype(str).eq(symbol)].copy()
    state_map = states.set_index("market_time_shanghai")[["state", "state_available_at"]]

    rows: list[dict[str, object]] = []
    for (day, segment), group in frame.groupby(["trading_day", "session_segment"], sort=False):
        group = group.sort_values("market_time_shanghai", kind="stable")
        by_minute = group.set_index("segment_minute")
        max_minute = int(group["segment_minute"].max())

        # Anchor to the physical segment start.  Exact t-h/t/t+h rows must all
        # exist, so repaired/removed minutes never get bridged by row position.
        for minute in range(horizon, max_minute - horizon + 1, horizon):
            if (
                minute - horizon not in by_minute.index
                or minute not in by_minute.index
                or minute + horizon not in by_minute.index
            ):
                continue

            previous = by_minute.loc[minute - horizon]
            current = by_minute.loc[minute]
            future = by_minute.loc[minute + horizon]
            if any(isinstance(item, pd.DataFrame) for item in (previous, current, future)):
                raise ValueError("duplicate segment-minute market rows")

            decision_time = current["market_time_shanghai"]
            if decision_time not in state_map.index:
                continue
            state_row = state_map.loc[decision_time]
            state = str(state_row["state"])
            if state not in ALLOWED_STATES:
                continue
            if state_row["state_available_at"] > decision_time:
                raise StatePoolError("state availability violation after exact merge")

            past_return = float(np.log(float(current["close"]) / float(previous["close"])))
            raw_signal = int(np.sign(past_return))
            position = raw_signal if family == "trend" else -raw_signal
            forward_return = float(np.log(float(future["close"]) / float(current["close"])))

            rows.append(
                {
                    "symbol": symbol,
                    "trading_day": str(day),
                    "session_segment": str(segment),
                    "market_time_shanghai": decision_time,
                    "state": state,
                    "horizon_minutes": horizon,
                    "family": family,
                    "position": position,
                    "gross_edge_bp": position * forward_return * 1e4,
                    "minute_of_segment": minute,
                    "clock_bucket_15m": int(minute // 15),
                }
            )

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out = out.sort_values(
        ["trading_day", "session_segment", "market_time_shanghai"], kind="stable"
    ).reset_index(drop=True)

    # A router entering/leaving a sampled state closes its old deployment.  Each
    # contiguous sampled-state run therefore starts/ends flat; sign changes inside
    # the run use actual |position_t-position_t-1| turnover.
    state_change = (
        out["state"].ne(out["state"].shift())
        | out["trading_day"].ne(out["trading_day"].shift())
        | out["session_segment"].ne(out["session_segment"].shift())
    )
    out["state_run_id"] = state_change.cumsum().astype("int64")
    out["turnover_units"] = 0.0

    for indices in out.groupby("state_run_id", sort=False).groups.values():
        loc = list(indices)
        positions = out.loc[loc, "position"].to_numpy(dtype=float)
        turnover = np.zeros(len(loc), dtype=float)
        turnover[0] += abs(positions[0])
        if len(loc) > 1:
            turnover[1:] += np.abs(np.diff(positions))
        turnover[-1] += abs(positions[-1])
        out.loc[loc, "turnover_units"] = turnover

    return out


def summarize_observations(observations: pd.DataFrame) -> pd.DataFrame:
    """Summarize gross edge, turnover and frozen fixed-cost survival metrics."""

    if observations.empty:
        return pd.DataFrame()

    rows: list[dict[str, object]] = []
    grouping = ["symbol", "state", "family", "horizon_minutes"]
    for (symbol, state, family, horizon), group in observations.groupby(grouping, sort=True):
        active = group["position"].ne(0)
        gross_sum = float(group["gross_edge_bp"].sum())
        turnover = float(group["turnover_units"].sum())
        day_means = group.groupby("trading_day")["gross_edge_bp"].mean()
        clustered_se = (
            float(day_means.std(ddof=1) / np.sqrt(len(day_means)))
            if len(day_means) > 1
            else np.nan
        )

        row: dict[str, object] = {
            "symbol": symbol,
            "state": state,
            "family": family,
            "horizon_minutes": int(horizon),
            "n_decisions": int(len(group)),
            "active_fraction": float(active.mean()),
            "mean_gross_edge_bp": float(group["gross_edge_bp"].mean()),
            "median_gross_edge_bp": float(group["gross_edge_bp"].median()),
            "win_rate_when_active": (
                float(group.loc[active, "gross_edge_bp"].gt(0).mean()) if active.any() else np.nan
            ),
            "gross_edge_day_cluster_SE": clustered_se,
            "turnover_units": turnover,
            "break_even_oneway_cost_bp": gross_sum / turnover if turnover > 0 else np.nan,
            "q05_signed_edge_bp": float(group["gross_edge_bp"].quantile(0.05)),
            "q01_signed_edge_bp": float(group["gross_edge_bp"].quantile(0.01)),
        }
        for cost in COST_GRID_BP:
            row[f"net_edge_bp_c{int(cost)}"] = (gross_sum - cost * turnover) / len(group)
        rows.append(row)

    return pd.DataFrame(rows).sort_values(grouping).reset_index(drop=True)
