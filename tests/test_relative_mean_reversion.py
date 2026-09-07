import numpy as np
import pandas as pd

from regime_lab.relative_mean_reversion import (
    RelativeMRConfig,
    align_pair,
    compute_relative_state,
    relative_diagnostic_return,
    relative_reentry_signal,
)


def _frame(symbol_shift=0.0, n=30):
    close = np.linspace(100.0 + symbol_shift, 103.0 + symbol_shift, n)
    times = pd.date_range("2024-01-02 09:35", periods=n, freq="5min", tz="Asia/Shanghai")
    return pd.DataFrame(
        {
            "trading_day": ["2024-01-02"] * n,
            "market_time_shanghai": times,
            "open": close - 0.05,
            "high": close + 0.1,
            "low": close - 0.1,
            "close": close,
        }
    )


def test_pair_alignment_is_one_to_one():
    star = _frame(0.0)
    csi = _frame(10.0)
    pair = align_pair(star, csi)

    assert len(pair) == len(star)
    assert {"star_open", "star_close", "csi_open", "csi_close"} <= set(pair.columns)


def test_relative_state_is_prefix_invariant():
    star = _frame(0.0, 80)
    csi = _frame(10.0, 80)
    # Inject deterministic relative oscillation into STAR only.
    star["close"] += np.sin(np.arange(80)) * 0.2
    star["open"] = star["close"] - 0.05
    star["high"] = star["close"] + 0.1
    star["low"] = star["close"] - 0.1
    pair = align_pair(star, csi)
    cfg = RelativeMRConfig(
        bar_minutes=5,
        dislocation_minutes=10,
        distribution_minutes=25,
        threshold=2.0,
    )

    full = compute_relative_state(pair, cfg)
    prefix = compute_relative_state(pair.iloc[:50], cfg)

    pd.testing.assert_frame_equal(full.iloc[:50], prefix, check_dtype=False)


def test_relative_dislocation_does_not_bridge_trading_day():
    star = _frame(0.0, 8)
    csi = _frame(10.0, 8)
    star.loc[4:, "trading_day"] = "2024-01-03"
    csi.loc[4:, "trading_day"] = "2024-01-03"
    pair = align_pair(star, csi)
    cfg = RelativeMRConfig(
        bar_minutes=5,
        dislocation_minutes=10,
        distribution_minutes=10,
        threshold=2.0,
    )

    state = compute_relative_state(pair, cfg)

    assert pd.isna(state.loc[4, "relative_move"])
    assert pd.isna(state.loc[5, "relative_move"])


def test_relative_reentry_direction():
    pair = pd.DataFrame({"trading_day": ["d"] * 5})
    state = pd.DataFrame({"relative_robust_z": [0.0, 2.5, 2.2, 1.5, 0.0]})
    cfg = RelativeMRConfig(
        bar_minutes=5,
        dislocation_minutes=5,
        distribution_minutes=10,
        threshold=2.0,
    )

    signal = relative_reentry_signal(pair, state, cfg)

    assert signal.tolist() == [0, 0, 0, -1, 0]


def test_relative_diagnostic_return_uses_next_open_and_equal_notional_spread():
    pair = pd.DataFrame(
        {
            "trading_day": ["d"] * 4,
            "star_open": [100.0, 101.0, 102.0, 103.0],
            "star_close": [100.0, 102.0, 104.0, 105.0],
            "csi_open": [200.0, 201.0, 202.0, 203.0],
            "csi_close": [200.0, 201.0, 202.0, 203.0],
        }
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    result = relative_diagnostic_return(pair, signal, holding_bars=2)
    expected = (104.0 / 101.0 - 1.0) - (202.0 / 201.0 - 1.0)

    assert result.iloc[0] == expected
