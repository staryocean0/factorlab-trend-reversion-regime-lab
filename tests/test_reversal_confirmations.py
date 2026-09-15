import pandas as pd

from regime_lab.reversal_confirmations import (
    mean_reversion_reentry_signal,
    structural_reversal_confirmation,
)


def test_mean_reversion_reentry_waits_until_extreme_crosses_back_inside_band():
    frame = pd.DataFrame({"trading_day": ["d"] * 4})
    features = pd.DataFrame({"stretch_atr": [1.0, 2.4, 1.8, 1.0]})

    signal = mean_reversion_reentry_signal(frame, features, stretch_threshold=2.0)

    assert signal.tolist() == [0, 0, -1, 0]


def test_mean_reversion_reentry_handles_downside_symmetrically():
    frame = pd.DataFrame({"trading_day": ["d"] * 4})
    features = pd.DataFrame({"stretch_atr": [-1.0, -2.4, -1.8, -1.0]})

    signal = mean_reversion_reentry_signal(frame, features, stretch_threshold=2.0)

    assert signal.tolist() == [0, 0, 1, 0]


def test_reentry_does_not_cross_trading_day():
    frame = pd.DataFrame({"trading_day": ["d1", "d1", "d2"]})
    features = pd.DataFrame({"stretch_atr": [1.0, 2.4, 1.8]})

    signal = mean_reversion_reentry_signal(frame, features, stretch_threshold=2.0)

    assert signal.abs().sum() == 0


def test_structural_short_requires_close_below_candidate_low():
    frame = pd.DataFrame(
        {
            "high": [101.0, 103.0, 102.0, 101.0],
            "low": [99.0, 100.0, 99.5, 99.0],
            "close": [100.0, 102.0, 99.0, 99.5],
            "trading_day": ["d"] * 4,
        }
    )
    candidate = pd.Series([0, -1, 0, 0], dtype="int8")

    signal = structural_reversal_confirmation(frame, candidate)

    assert signal.iloc[1] == 0
    assert signal.iloc[2] == -1


def test_structural_long_requires_close_above_candidate_high():
    frame = pd.DataFrame(
        {
            "high": [101.0, 102.0, 103.0, 104.0],
            "low": [99.0, 98.0, 99.0, 100.0],
            "close": [100.0, 99.0, 102.5, 103.0],
            "trading_day": ["d"] * 4,
        }
    )
    candidate = pd.Series([0, 1, 0, 0], dtype="int8")

    signal = structural_reversal_confirmation(frame, candidate)

    assert signal.iloc[2] == 1
