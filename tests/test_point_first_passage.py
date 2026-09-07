import pandas as pd

from regime_lab.point_first_passage import resolve_point_first_passage


def _obs(prices, *, duplicate_first=False):
    times = pd.date_range("2025-01-02 09:35:00", periods=len(prices), freq="3s", tz="Asia/Shanghai")
    frame = pd.DataFrame({"market_time_shanghai": times, "price": prices})
    if duplicate_first:
        extra = pd.DataFrame({"market_time_shanghai": [times[1]], "price": [98.8]})
        frame = pd.concat([frame, extra], ignore_index=True).sort_values("market_time_shanghai")
    return frame.reset_index(drop=True)


def test_long_target_first():
    frame = _obs([100.0, 100.05, 100.11, 99.95])
    result = resolve_point_first_passage(
        frame,
        entry_time=frame.loc[0, "market_time_shanghai"],
        end_time=frame.loc[3, "market_time_shanghai"],
        entry_price=100.0,
        direction=1,
        barrier_bps=10.0,
    )
    assert result.outcome == "target_first"
    assert result.trigger_time == frame.loc[2, "market_time_shanghai"]


def test_long_stop_first():
    frame = _obs([100.0, 99.85, 100.2])
    result = resolve_point_first_passage(
        frame,
        entry_time=frame.loc[0, "market_time_shanghai"],
        end_time=frame.loc[2, "market_time_shanghai"],
        entry_price=100.0,
        direction=1,
        barrier_bps=10.0,
    )
    assert result.outcome == "stop_first"


def test_no_observed_cross_does_not_invent_extrema():
    frame = _obs([100.0, 100.05, 99.95, 100.02])
    result = resolve_point_first_passage(
        frame,
        entry_time=frame.loc[0, "market_time_shanghai"],
        end_time=frame.loc[3, "market_time_shanghai"],
        entry_price=100.0,
        direction=1,
        barrier_bps=10.0,
    )
    assert result.outcome == "no_observed_cross"
    assert result.trigger_time is None


def test_duplicate_timestamp_both_sides_is_adverse_ambiguous():
    t0 = pd.Timestamp("2025-01-02 09:35:00", tz="Asia/Shanghai")
    t1 = t0 + pd.Timedelta(seconds=3)
    frame = pd.DataFrame(
        {
            "market_time_shanghai": [t0, t1, t1],
            "price": [100.0, 100.2, 99.8],
        }
    )
    result = resolve_point_first_passage(
        frame,
        entry_time=t0,
        end_time=t1,
        entry_price=100.0,
        direction=1,
        barrier_bps=10.0,
    )
    assert result.outcome == "ambiguous_stop_assumed"
    assert result.trigger_time == t1


def test_short_direction_is_symmetric():
    frame = _obs([100.0, 99.88, 100.2])
    result = resolve_point_first_passage(
        frame,
        entry_time=frame.loc[0, "market_time_shanghai"],
        end_time=frame.loc[2, "market_time_shanghai"],
        entry_price=100.0,
        direction=-1,
        barrier_bps=10.0,
    )
    assert result.outcome == "target_first"
