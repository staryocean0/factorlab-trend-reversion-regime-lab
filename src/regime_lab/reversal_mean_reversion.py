"""Causal baseline measurements for reversal and mean-reversion research.

The module intentionally does not implement a trend-following strategy or a
trend-vs-reversion gate.  Signals are computed at the close of bar t and any
diagnostic return enters no earlier than the open of bar t+1.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ReversalFeatureConfig:
    """Physical-horizon configuration expressed in trading minutes."""

    bar_minutes: int = 5
    anchor_minutes: int = 120
    atr_minutes: int = 120
    range_minutes: int = 60
    leg_minutes: int = 60
    shock_minutes: int = 60

    def __post_init__(self) -> None:
        fields = (
            "bar_minutes",
            "anchor_minutes",
            "atr_minutes",
            "range_minutes",
            "leg_minutes",
            "shock_minutes",
        )
        if any(getattr(self, name) <= 0 for name in fields):
            raise ValueError("all minute settings must be positive")
        for name in fields[1:]:
            if getattr(self, name) % self.bar_minutes:
                raise ValueError(f"{name} must be divisible by bar_minutes")

    @property
    def anchor_window(self) -> int:
        return self.anchor_minutes // self.bar_minutes

    @property
    def atr_window(self) -> int:
        return self.atr_minutes // self.bar_minutes

    @property
    def range_window(self) -> int:
        return self.range_minutes // self.bar_minutes

    @property
    def leg_window(self) -> int:
        return self.leg_minutes // self.bar_minutes

    @property
    def shock_window(self) -> int:
        return self.shock_minutes // self.bar_minutes


def _numeric(frame: pd.DataFrame, name: str) -> pd.Series:
    return pd.to_numeric(frame[name], errors="coerce").astype(float)


def compute_reversal_features(
    frame: pd.DataFrame,
    config: ReversalFeatureConfig = ReversalFeatureConfig(),
) -> pd.DataFrame:
    """Compute past-only features at each completed bar.

    The causal anchor, ATR scale, and prior breakout range all exclude the
    current bar. Current-bar OHLC is allowed because the signal is defined at
    that bar's close.
    """

    required = {"open", "high", "low", "close"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"missing required OHLC columns: {sorted(missing)}")

    open_ = _numeric(frame, "open")
    high = _numeric(frame, "high")
    low = _numeric(frame, "low")
    close = _numeric(frame, "close")

    max_oc = pd.concat([open_, close], axis=1).max(axis=1)
    min_oc = pd.concat([open_, close], axis=1).min(axis=1)
    invalid = (high < max_oc) | (low > min_oc) | (high < low)
    if invalid.fillna(False).any():
        raise ValueError("invalid OHLC geometry")

    out = pd.DataFrame(index=frame.index)

    log_close = np.log(close.where(close > 0))
    ret = log_close.diff()
    prev_close = close.shift(1)
    true_range = pd.concat(
        [
            (high - low).abs(),
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    out["anchor"] = close.shift(1).ewm(
        span=config.anchor_window,
        adjust=False,
        min_periods=config.anchor_window,
    ).mean()
    out["atr_past"] = true_range.shift(1).rolling(
        config.atr_window,
        min_periods=config.atr_window,
    ).mean()
    out["stretch_atr"] = (close - out["anchor"]) / out["atr_past"]

    out["prior_high"] = high.shift(1).rolling(
        config.range_window,
        min_periods=config.range_window,
    ).max()
    out["prior_low"] = low.shift(1).rolling(
        config.range_window,
        min_periods=config.range_window,
    ).min()

    out["break_above"] = high.gt(out["prior_high"]).fillna(False)
    out["break_below"] = low.lt(out["prior_low"]).fillna(False)
    out["failed_break_above"] = (
        out["break_above"] & close.le(out["prior_high"])
    ).fillna(False)
    out["failed_break_below"] = (
        out["break_below"] & close.ge(out["prior_low"])
    ).fillna(False)

    bar_range = (high - low).replace(0, np.nan)
    out["upper_wick_ratio"] = ((high - max_oc) / bar_range).clip(0, 1)
    out["lower_wick_ratio"] = ((min_oc - low) / bar_range).clip(0, 1)
    out["clv"] = ((2 * close - high - low) / bar_range).clip(-1, 1)

    leg_return = log_close - log_close.shift(config.leg_window)
    path_length = ret.abs().rolling(
        config.leg_window,
        min_periods=config.leg_window,
    ).sum()
    out["leg_return"] = leg_return
    out["leg_direction"] = np.sign(leg_return)
    out["leg_efficiency"] = (leg_return.abs() / path_length).clip(0, 1)
    out["leg_displacement_atr"] = (
        close - close.shift(config.leg_window)
    ) / out["atr_past"]

    shock_path = ret.abs().rolling(
        config.shock_window,
        min_periods=config.shock_window,
    ).sum()
    out["shock_concentration"] = (ret.abs() / shock_path).clip(0, 1)

    if "amount" in frame.columns:
        amount = _numeric(frame, "amount")
        log_amount = np.log(amount.where(amount > 0))
        past_amount = log_amount.shift(1)
        window = config.anchor_window
        median = past_amount.rolling(window, min_periods=window).median()
        mad = past_amount.rolling(window, min_periods=window).apply(
            lambda x: np.median(np.abs(x - np.median(x))),
            raw=True,
        )
        out["amount_robust_z"] = (
            (log_amount - median) / (1.4826 * mad.replace(0, np.nan))
        )

    return out


def mean_reversion_signal(
    features: pd.DataFrame,
    *,
    stretch_threshold: float = 2.0,
    require_failed_acceptance: bool = False,
) -> pd.Series:
    """MR0/MR1 signal: fade an extreme causal-anchor displacement.

    +1 means long, -1 short, 0 no signal.  With
    ``require_failed_acceptance=True`` the signal additionally requires a
    failed break of the lagged range in the direction of the stretch.
    """

    if stretch_threshold <= 0:
        raise ValueError("stretch_threshold must be positive")

    stretch = pd.to_numeric(features["stretch_atr"], errors="coerce")
    long = stretch.le(-stretch_threshold)
    short = stretch.ge(stretch_threshold)

    if require_failed_acceptance:
        long &= features["failed_break_below"].fillna(False)
        short &= features["failed_break_above"].fillna(False)

    signal = pd.Series(0, index=features.index, dtype="int8")
    signal.loc[long] = 1
    signal.loc[short] = -1
    return signal


def trend_reversal_signal(
    features: pd.DataFrame,
    *,
    min_leg_efficiency: float = 0.60,
    min_leg_displacement_atr: float = 1.50,
) -> pd.Series:
    """REV0 signal: fade a failed breakout after an established directional leg.

    This is a reversal strategy baseline, not a trend-following strategy.
    """

    if not 0 <= min_leg_efficiency <= 1:
        raise ValueError("min_leg_efficiency must be between 0 and 1")
    if min_leg_displacement_atr <= 0:
        raise ValueError("min_leg_displacement_atr must be positive")

    efficiency = pd.to_numeric(features["leg_efficiency"], errors="coerce")
    displacement = pd.to_numeric(
        features["leg_displacement_atr"], errors="coerce"
    )

    long = (
        efficiency.ge(min_leg_efficiency)
        & displacement.le(-min_leg_displacement_atr)
        & features["failed_break_below"].fillna(False)
    )
    short = (
        efficiency.ge(min_leg_efficiency)
        & displacement.ge(min_leg_displacement_atr)
        & features["failed_break_above"].fillna(False)
    )

    signal = pd.Series(0, index=features.index, dtype="int8")
    signal.loc[long] = 1
    signal.loc[short] = -1
    return signal


def one_bar_directional_confirmation(
    frame: pd.DataFrame,
    candidate_signal: pd.Series,
    *,
    require_same_trading_day: bool = True,
) -> pd.Series:
    """Confirm a prior-bar candidate with one completed bar in fade direction.

    A candidate observed at close ``t-1`` becomes a confirmed signal at close
    ``t`` only when the close-to-close move of bar ``t`` is in the candidate's
    intended reversal direction.  Confirmed entry may therefore occur no
    earlier than open ``t+1``.

    No magnitude threshold is introduced: this isolates confirmation timing
    from threshold optimization.
    """

    if len(frame) != len(candidate_signal):
        raise ValueError("frame and candidate_signal length mismatch")
    close = _numeric(frame, "close")
    candidate = candidate_signal.shift(1).fillna(0).astype("int8")
    move = close / close.shift(1) - 1.0
    confirmed = candidate.ne(0) & (candidate.astype(float) * move > 0)

    if require_same_trading_day:
        if "trading_day" not in frame.columns:
            raise ValueError("trading_day required for same-day confirmation")
        day = frame["trading_day"].astype(str)
        confirmed &= day.eq(day.shift(1))

    signal = pd.Series(0, index=frame.index, dtype="int8")
    signal.loc[confirmed] = candidate.loc[confirmed]
    return signal


def diagnostic_event_return(
    frame: pd.DataFrame,
    signal: pd.Series,
    *,
    holding_bars: int,
    same_trading_day: bool = True,
) -> pd.Series:
    """Gross diagnostic event return using next-bar-open entry.

    A signal observed at close t enters at open t+1 and exits at close t+h.
    This deliberately avoids same-bar execution assumptions.  It is still an
    index-direction diagnostic, not a tradable-cash-index backtest.
    """

    if holding_bars < 1:
        raise ValueError("holding_bars must be >= 1")

    entry = _numeric(frame, "open").shift(-1)
    exit_ = _numeric(frame, "close").shift(-holding_bars)
    result = signal.astype(float) * (exit_ / entry - 1)

    if same_trading_day and "trading_day" in frame.columns:
        day = frame["trading_day"].astype(str)
        valid = day.shift(-1).eq(day) & day.shift(-holding_bars).eq(day)
        result = result.where(valid)

    return result.where(signal.ne(0))


def frozen_anchor_hit_bars(
    frame: pd.DataFrame,
    features: pd.DataFrame,
    signal: pd.Series,
    *,
    max_bars: int,
    same_trading_day: bool = True,
) -> pd.Series:
    """First future bar that touches the anchor frozen at signal time.

    Long signals are considered reverted when a future high reaches the frozen
    anchor; short signals when a future low reaches it.  The result is a
    nullable integer number of bars and is a research outcome, not a feature.
    """

    if max_bars < 1:
        raise ValueError("max_bars must be >= 1")

    anchor = pd.to_numeric(features["anchor"], errors="coerce")
    result = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    active = signal.ne(0) & anchor.notna()

    if same_trading_day and "trading_day" in frame.columns:
        day = frame["trading_day"].astype(str)
    else:
        day = None

    for bars in range(1, max_bars + 1):
        future_high = _numeric(frame, "high").shift(-bars)
        future_low = _numeric(frame, "low").shift(-bars)
        hit = (
            signal.gt(0) & future_high.ge(anchor)
        ) | (
            signal.lt(0) & future_low.le(anchor)
        )
        if day is not None:
            hit &= day.shift(-bars).eq(day)
        choose = active & result.isna() & hit
        result.loc[choose] = bars

    return result
