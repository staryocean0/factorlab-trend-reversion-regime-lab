"""Cross-index relative-value mean-reversion measurements.

The module studies STAR50 vs CSI1000 relative dislocations. It does not import
or construct a trend-following policy. All state is causal and all diagnostic
entries occur no earlier than the next bar open.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RelativeMRConfig:
    bar_minutes: int = 5
    dislocation_minutes: int = 60
    distribution_minutes: int = 240
    threshold: float = 2.0

    def __post_init__(self) -> None:
        if self.bar_minutes <= 0:
            raise ValueError("bar_minutes must be positive")
        for name in ("dislocation_minutes", "distribution_minutes"):
            value = getattr(self, name)
            if value <= 0 or value % self.bar_minutes:
                raise ValueError(f"{name} must be a positive multiple of bar_minutes")
        if self.threshold <= 0:
            raise ValueError("threshold must be positive")

    @property
    def dislocation_bars(self) -> int:
        return self.dislocation_minutes // self.bar_minutes

    @property
    def distribution_observations(self) -> int:
        """Number of valid completed dislocation observations used for scale."""
        return self.distribution_minutes // self.bar_minutes


def align_pair(star: pd.DataFrame, csi: pd.DataFrame) -> pd.DataFrame:
    """Inner-align the two supplied index bars on trading day and market time."""
    keys = ["trading_day", "market_time_shanghai"]
    required = set(keys + ["open", "close"])
    for name, frame in (("star", star), ("csi", csi)):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} missing columns: {sorted(missing)}")
        if frame.duplicated(keys).any():
            raise ValueError(f"{name} contains duplicate pair keys")

    left = star[keys + ["open", "high", "low", "close"]].rename(
        columns={c: f"star_{c}" for c in ["open", "high", "low", "close"]}
    )
    right = csi[keys + ["open", "high", "low", "close"]].rename(
        columns={c: f"csi_{c}" for c in ["open", "high", "low", "close"]}
    )
    out = left.merge(right, on=keys, how="inner", validate="one_to_one")
    return out.sort_values(keys, kind="stable").reset_index(drop=True)


def _last_valid_robust_stats(
    prior_series: pd.Series,
    observations: int,
) -> tuple[pd.Series, pd.Series]:
    """Median/MAD of the most recent N finite prior observations."""
    if observations < 2:
        raise ValueError("observations must be >= 2")

    location = pd.Series(np.nan, index=prior_series.index, dtype=float)
    scale = pd.Series(np.nan, index=prior_series.index, dtype=float)
    history: deque[float] = deque(maxlen=observations)

    for idx, value in prior_series.items():
        if pd.notna(value) and np.isfinite(value):
            history.append(float(value))
        if len(history) == observations:
            arr = np.asarray(history, dtype=float)
            median = float(np.median(arr))
            mad = float(np.median(np.abs(arr - median)))
            location.loc[idx] = median
            scale.loc[idx] = 1.4826 * mad

    return location, scale


def compute_relative_state(
    pair: pd.DataFrame,
    config: RelativeMRConfig = RelativeMRConfig(),
) -> pd.DataFrame:
    """Measure same-day relative return dislocation and robust prior z-score.

    The dislocation is the STAR-minus-CSI log return over the configured
    physical lookback. If the lookback crosses a trading-day boundary it is
    undefined. The robust location and scale use the most recent configured
    number of valid, strictly prior dislocation observations.
    """
    required = {"trading_day", "star_close", "csi_close"}
    missing = required - set(pair.columns)
    if missing:
        raise ValueError(f"missing pair-state columns: {sorted(missing)}")

    star = pd.to_numeric(pair["star_close"], errors="coerce").astype(float)
    csi = pd.to_numeric(pair["csi_close"], errors="coerce").astype(float)
    if (star.dropna() <= 0).any() or (csi.dropna() <= 0).any():
        raise ValueError("pair closes must be positive")

    k = config.dislocation_bars
    day = pair["trading_day"].astype(str)
    same_day_lookback = day.eq(day.shift(k))
    relative_move = (
        (np.log(star) - np.log(star.shift(k)))
        - (np.log(csi) - np.log(csi.shift(k)))
    ).where(same_day_lookback)

    prior = relative_move.shift(1)
    location, scale = _last_valid_robust_stats(
        prior,
        config.distribution_observations,
    )
    z = (relative_move - location) / scale.replace(0, np.nan)

    return pd.DataFrame(
        {
            "relative_move": relative_move,
            "prior_location": location,
            "prior_scale": scale,
            "relative_robust_z": z,
        },
        index=pair.index,
    )


def relative_reentry_signal(
    pair: pd.DataFrame,
    state: pd.DataFrame,
    config: RelativeMRConfig = RelativeMRConfig(),
) -> pd.Series:
    """Trade only after a relative extreme crosses back inside the robust band.

    +1 means long STAR / short CSI. -1 means short STAR / long CSI.
    """
    if len(pair) != len(state):
        raise ValueError("pair and state length mismatch")
    if "relative_robust_z" not in state.columns:
        raise ValueError("relative_robust_z is required")

    z = pd.to_numeric(state["relative_robust_z"], errors="coerce")
    prev = z.shift(1)
    day = pair["trading_day"].astype(str)
    same_day = day.eq(day.shift(1))

    long_spread = same_day & prev.le(-config.threshold) & z.gt(-config.threshold)
    short_spread = same_day & prev.ge(config.threshold) & z.lt(config.threshold)

    signal = pd.Series(0, index=pair.index, dtype="int8")
    signal.loc[long_spread] = 1
    signal.loc[short_spread] = -1
    return signal


def relative_diagnostic_return(
    pair: pd.DataFrame,
    signal: pd.Series,
    *,
    holding_bars: int,
) -> pd.Series:
    """Equal-notional two-leg gross diagnostic return.

    Signal at close t enters both legs at open t+1 and exits at close t+h.
    Return is STAR simple return minus CSI simple return, multiplied by signal.
    Cross-day horizons are masked. Financing, spread, fees and impact are not
    included and must be added before any economic strategy claim.
    """
    if holding_bars < 1:
        raise ValueError("holding_bars must be >= 1")
    if len(pair) != len(signal):
        raise ValueError("pair and signal length mismatch")

    required = {"trading_day", "star_open", "star_close", "csi_open", "csi_close"}
    missing = required - set(pair.columns)
    if missing:
        raise ValueError(f"missing diagnostic columns: {sorted(missing)}")

    star_entry = pd.to_numeric(pair["star_open"], errors="coerce").shift(-1)
    csi_entry = pd.to_numeric(pair["csi_open"], errors="coerce").shift(-1)
    star_exit = pd.to_numeric(pair["star_close"], errors="coerce").shift(-holding_bars)
    csi_exit = pd.to_numeric(pair["csi_close"], errors="coerce").shift(-holding_bars)

    star_r = star_exit / star_entry - 1.0
    csi_r = csi_exit / csi_entry - 1.0
    result = signal.astype(float) * (star_r - csi_r)

    day = pair["trading_day"].astype(str)
    valid = day.shift(-1).eq(day) & day.shift(-holding_bars).eq(day)
    return result.where(valid & signal.ne(0))
