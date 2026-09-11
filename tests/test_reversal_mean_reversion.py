import numpy as np
import pandas as pd

from regime_lab.reversal_mean_reversion import (
    ReversalFeatureConfig,
    compute_reversal_features,
    diagnostic_event_return,
    frozen_anchor_hit_bars,
    mean_reversion_signal,
    one_bar_directional_confirmation,
    trend_reversal_signal,
)


def _rising_frame(n=80):
    close = np.linspace(100.0, 140.0, n)
    return pd.DataFrame(
        {
            "open": close - 0.1,
            "high": close + 0.3,
            "low": close - 0.3,
            "close": close,
            "amount": np.linspace(1e9, 1.2e9, n),
            "trading_day": ["2024-01-02"] * n,
        }
    )


def _small_config():
    return ReversalFeatureConfig(
        bar_minutes=5,
        anchor_minutes=25,
        atr_minutes=25,
        range_minutes=15,
        leg_minutes=15,
        shock_minutes=15,
    )


def test_monotone_path_is_efficient_but_not_a_reversal_without_failure():
    frame = _rising_frame()
    features = compute_reversal_features(frame, _small_config())

    assert (features["leg_efficiency"].dropna() > 0.99).all()
    signal = trend_reversal_signal(
        features,
        min_leg_efficiency=0.5,
        min_leg_displacement_atr=0.5,
    )
    assert signal.abs().sum() == 0


def test_failed_upside_break_after_rising_leg_produces_short_reversal():
    frame = _rising_frame(20)
    prior_high = frame["high"].iloc[-4:-1].max()
    i = frame.index[-1]
    frame.loc[i, ["open", "high", "low", "close"]] = [
        prior_high + 0.05,
        prior_high + 1.0,
        prior_high - 0.5,
        prior_high - 0.1,
    ]

    features = compute_reversal_features(frame, _small_config())
    signal = trend_reversal_signal(
        features,
        min_leg_efficiency=0.5,
        min_leg_displacement_atr=0.5,
    )

    assert features["failed_break_above"].iloc[-1]
    assert signal.iloc[-1] == -1


def test_mean_reversion_confirmation_requires_failed_acceptance():
    frame = _rising_frame()
    features = compute_reversal_features(frame, _small_config())

    raw = mean_reversion_signal(features, stretch_threshold=1.0)
    confirmed = mean_reversion_signal(
        features,
        stretch_threshold=1.0,
        require_failed_acceptance=True,
    )

    assert (raw == -1).any()
    assert confirmed.abs().sum() == 0


def test_features_are_prefix_invariant():
    frame = _rising_frame()
    config = _small_config()

    full = compute_reversal_features(frame, config)
    prefix = compute_reversal_features(frame.iloc[:50], config)

    pd.testing.assert_frame_equal(
        full.iloc[:50],
        prefix,
        check_dtype=False,
    )


def test_one_bar_confirmation_occurs_only_after_intended_direction_bar_closes():
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 101.0],
            "high": [101.0, 103.0, 102.5, 101.5],
            "low": [99.0, 100.5, 100.5, 100.0],
            "close": [100.0, 102.0, 101.0, 100.5],
            "trading_day": ["d"] * 4,
        }
    )
    candidate = pd.Series([0, -1, 0, 0], dtype="int8")

    confirmed = one_bar_directional_confirmation(frame, candidate)

    assert confirmed.iloc[1] == 0
    assert confirmed.iloc[2] == -1


def test_one_bar_confirmation_does_not_cross_trading_day():
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 100.0],
            "high": [101.0, 102.0, 100.5],
            "low": [99.0, 100.0, 99.0],
            "close": [100.0, 101.0, 99.5],
            "trading_day": ["d1", "d1", "d2"],
        }
    )
    candidate = pd.Series([0, -1, 0], dtype="int8")

    confirmed = one_bar_directional_confirmation(frame, candidate)

    assert confirmed.abs().sum() == 0


def test_diagnostic_return_enters_next_bar_open():
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.0, 102.0, 103.0, 104.0],
            "trading_day": ["d"] * 4,
        }
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    result = diagnostic_event_return(frame, signal, holding_bars=2)

    assert result.iloc[0] == (103.0 / 101.0 - 1.0)


def test_frozen_anchor_hit_uses_signal_time_anchor():
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0, 103.0],
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 100.0, 101.0, 102.0],
            "close": [100.0, 102.0, 103.0, 104.0],
            "trading_day": ["d"] * 4,
        }
    )
    features = pd.DataFrame({"anchor": [103.0, np.nan, np.nan, np.nan]})
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    hit = frozen_anchor_hit_bars(
        frame,
        features,
        signal,
        max_bars=3,
    )

    assert hit.iloc[0] == 2


def test_same_day_guard_masks_cross_day_diagnostic_return():
    frame = pd.DataFrame(
        {
            "open": [100.0, 101.0, 102.0],
            "high": [101.0, 102.0, 103.0],
            "low": [99.0, 100.0, 101.0],
            "close": [100.0, 102.0, 103.0],
            "trading_day": ["d1", "d2", "d2"],
        }
    )
    signal = pd.Series([1, 0, 0], dtype="int8")

    result = diagnostic_event_return(frame, signal, holding_bars=1)

    assert pd.isna(result.iloc[0])
