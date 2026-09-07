import pandas as pd

from regime_lab.first_passage import symmetric_first_passage


def _frame(highs, lows, *, days=None):
    n = len(highs)
    if days is None:
        days = ["2024-01-02"] * n
    return pd.DataFrame(
        {
            "trading_day": days,
            "open": [100.0] * n,
            "high": highs,
            "low": lows,
        }
    )


def test_long_target_first_uses_next_bar_open():
    frame = _frame(
        [100.01, 100.06, 100.02, 100.01],
        [99.99, 99.98, 99.98, 99.99],
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert out.loc[0, "entry_price"] == 100.0
    assert out.loc[0, "outcome"] == "target_first"
    assert out.loc[0, "resolution_bars"] == 1


def test_long_stop_first():
    frame = _frame(
        [100.01, 100.02, 100.08, 100.01],
        [99.99, 99.94, 99.98, 99.99],
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert out.loc[0, "outcome"] == "stop_first"
    assert out.loc[0, "resolution_bars"] == 1


def test_same_bar_target_and_stop_is_ambiguous_not_favourable():
    frame = _frame(
        [100.01, 100.06, 100.01, 100.01],
        [99.99, 99.94, 99.99, 99.99],
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert out.loc[0, "outcome"] == "ambiguous_same_bar"
    assert out.loc[0, "resolution_bars"] == 1


def test_short_target_and_stop_are_direction_symmetric():
    frame = _frame(
        [100.01, 100.02, 100.01, 100.01],
        [99.99, 99.94, 99.99, 99.99],
    )
    signal = pd.Series([-1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert out.loc[0, "outcome"] == "target_first"


def test_full_horizon_must_remain_in_same_trading_day():
    frame = _frame(
        [100.01, 100.06, 100.01, 100.01],
        [99.99, 99.98, 99.99, 99.99],
        days=["2024-01-02", "2024-01-02", "2024-01-03", "2024-01-03"],
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert not bool(out.loc[0, "valid"])
    assert pd.isna(out.loc[0, "outcome"])


def test_neither_when_no_barrier_is_touched():
    frame = _frame(
        [100.01, 100.02, 100.03, 100.01],
        [99.99, 99.98, 99.97, 99.99],
    )
    signal = pd.Series([1, 0, 0, 0], dtype="int8")

    out = symmetric_first_passage(frame, signal, barrier_bps=5, horizon_bars=2)

    assert out.loc[0, "outcome"] == "neither"
    assert pd.isna(out.loc[0, "resolution_bars"])
