import pandas as pd

from regime_lab.barrier_policy import evaluate_barrier_timeout_policy


def _frame(highs, lows, closes=None, days=None):
    n = len(highs)
    if closes is None:
        closes = [100.0] * n
    if days is None:
        days = ["2025-01-02"] * n
    return pd.DataFrame(
        {
            "trading_day": days,
            "open": [100.0] * n,
            "high": highs,
            "low": lows,
            "close": closes,
        }
    )


def test_target_first_scores_positive_barrier():
    frame = _frame([100.01, 100.11, 100.01], [99.99, 99.99, 99.99])
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([1, 0, 0]), barrier_bps=10, horizon_bars=1
    )
    assert out.loc[0, "outcome"] == "target_first"
    assert out.loc[0, "gross_policy_bps"] == 10.0


def test_stop_first_scores_negative_barrier():
    frame = _frame([100.01, 100.01, 100.01], [99.99, 99.89, 99.99])
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([1, 0, 0]), barrier_bps=10, horizon_bars=1
    )
    assert out.loc[0, "outcome"] == "stop_first"
    assert out.loc[0, "gross_policy_bps"] == -10.0


def test_same_bar_both_is_conservative_stop():
    frame = _frame([100.01, 100.11, 100.01], [99.99, 99.89, 99.99])
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([1, 0, 0]), barrier_bps=10, horizon_bars=1
    )
    assert out.loc[0, "outcome"] == "ambiguous_stop_assumed"
    assert out.loc[0, "gross_policy_bps"] == -10.0


def test_timeout_uses_cap_close():
    frame = _frame(
        [100.01, 100.05, 100.05, 100.01],
        [99.99, 99.95, 99.95, 99.99],
        closes=[100.0, 100.02, 100.03, 100.0],
    )
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([1, 0, 0, 0]), barrier_bps=10, horizon_bars=2
    )
    assert out.loc[0, "outcome"] == "time_out"
    assert abs(out.loc[0, "gross_policy_bps"] - 3.0) < 1e-9


def test_short_policy_is_direction_symmetric():
    frame = _frame([100.01, 100.01, 100.01], [99.99, 99.89, 99.99])
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([-1, 0, 0]), barrier_bps=10, horizon_bars=1
    )
    assert out.loc[0, "outcome"] == "target_first"
    assert out.loc[0, "gross_policy_bps"] == 10.0


def test_cross_day_full_horizon_is_invalid():
    frame = _frame(
        [100.01, 100.11, 100.01],
        [99.99, 99.99, 99.99],
        days=["2025-01-02", "2025-01-02", "2025-01-03"],
    )
    out = evaluate_barrier_timeout_policy(
        frame, pd.Series([1, 0, 0]), barrier_bps=10, horizon_bars=2
    )
    assert not bool(out.loc[0, "valid"])
    assert pd.isna(out.loc[0, "outcome"])
