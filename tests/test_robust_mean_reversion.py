import numpy as np
import pandas as pd

from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)


def test_robust_residual_state_is_prefix_invariant():
    n = 80
    close = pd.Series(np.linspace(100.0, 110.0, n) + np.sin(np.arange(n)))
    frame = pd.DataFrame(
        {
            "close": close,
            "trading_day": ["d"] * n,
        }
    )
    base = pd.DataFrame({"anchor": close.ewm(span=10, adjust=False).mean().shift(1)})
    cfg = RobustResidualConfig(bar_minutes=5, distribution_minutes=50, threshold=2.0)

    full = compute_robust_residual_state(frame, base, cfg)
    prefix = compute_robust_residual_state(frame.iloc[:50], base.iloc[:50], cfg)

    pd.testing.assert_frame_equal(full.iloc[:50], prefix, check_dtype=False)


def test_robust_reentry_waits_for_cross_back_inside_band():
    frame = pd.DataFrame({"trading_day": ["d"] * 5})
    state = pd.DataFrame({"residual_robust_z": [0.0, 2.5, 2.2, 1.8, 1.0]})
    cfg = RobustResidualConfig(bar_minutes=5, distribution_minutes=10, threshold=2.0)

    signal = robust_residual_reentry_signal(frame, state, cfg)

    assert signal.tolist() == [0, 0, 0, -1, 0]


def test_robust_reentry_is_symmetric_and_does_not_cross_day():
    frame = pd.DataFrame({"trading_day": ["d1", "d1", "d2", "d2"]})
    state = pd.DataFrame({"residual_robust_z": [0.0, -2.5, -1.5, -1.0]})
    cfg = RobustResidualConfig(bar_minutes=5, distribution_minutes=10, threshold=2.0)

    signal = robust_residual_reentry_signal(frame, state, cfg)

    assert signal.abs().sum() == 0
