"""Robust residual state for strategy-first mean-reversion research."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RobustResidualConfig:
    """One-session robust residual distribution by default."""

    bar_minutes: int = 5
    distribution_minutes: int = 240
    threshold: float = 2.0

    def __post_init__(self) -> None:
        if self.bar_minutes <= 0 or self.distribution_minutes <= 0:
            raise ValueError("minute settings must be positive")
        if self.distribution_minutes % self.bar_minutes:
            raise ValueError("distribution_minutes must be divisible by bar_minutes")
        if self.threshold <= 0:
            raise ValueError("threshold must be positive")

    @property
    def window(self) -> int:
        return self.distribution_minutes // self.bar_minutes


def compute_robust_residual_state(
    frame: pd.DataFrame,
    base_features: pd.DataFrame,
    config: RobustResidualConfig = RobustResidualConfig(),
) -> pd.DataFrame:
    """Standardize current anchor residual by its strictly-prior distribution.

    ``base_features['anchor']`` is already causal.  Let residual be
    ``close-anchor``.  The state at completed bar t uses the median and MAD of
    residuals through t-1 only.  This asks whether the current displacement is
    unusual relative to recent *anchor residual behavior*, rather than how many
    single-bar ATRs price sits from the anchor.
    """

    if len(frame) != len(base_features):
        raise ValueError("frame and base_features length mismatch")
    if "close" not in frame.columns or "anchor" not in base_features.columns:
        raise ValueError("close and causal anchor are required")

    close = pd.to_numeric(frame["close"], errors="coerce").astype(float)
    anchor = pd.to_numeric(base_features["anchor"], errors="coerce").astype(float)
    residual = close - anchor
    prior = residual.shift(1)

    location = prior.rolling(config.window, min_periods=config.window).median()
    mad = prior.rolling(config.window, min_periods=config.window).apply(
        lambda x: np.median(np.abs(x - np.median(x))),
        raw=True,
    )
    scale = 1.4826 * mad
    z = (residual - location) / scale.replace(0, np.nan)

    return pd.DataFrame(
        {
            "residual": residual,
            "prior_residual_location": location,
            "prior_residual_scale": scale,
            "residual_robust_z": z,
        },
        index=frame.index,
    )


def robust_residual_reentry_signal(
    frame: pd.DataFrame,
    residual_state: pd.DataFrame,
    config: RobustResidualConfig = RobustResidualConfig(),
) -> pd.Series:
    """Enter only after a robust residual extreme crosses back inside its band.

    Previous bar outside +threshold followed by current bar back inside -> short.
    Previous bar outside -threshold followed by current bar back inside -> long.
    Signal forms at the current close and is therefore executable no earlier
    than the next bar open.
    """

    if len(frame) != len(residual_state):
        raise ValueError("frame and residual_state length mismatch")
    if "trading_day" not in frame.columns:
        raise ValueError("trading_day is required")
    if "residual_robust_z" not in residual_state.columns:
        raise ValueError("residual_robust_z is required")

    z = pd.to_numeric(residual_state["residual_robust_z"], errors="coerce")
    prev = z.shift(1)
    day = frame["trading_day"].astype(str)
    same_day = day.eq(day.shift(1))

    long = same_day & prev.le(-config.threshold) & z.gt(-config.threshold)
    short = same_day & prev.ge(config.threshold) & z.lt(config.threshold)

    signal = pd.Series(0, index=frame.index, dtype="int8")
    signal.loc[long] = 1
    signal.loc[short] = -1
    return signal
