from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from regime_lab.state_frequency_adaptation import (
    StatePoolError,
    build_frequency_observations,
    summarize_observations,
    validate_state_pool,
)


def _market(*, start="2025-01-02 09:30", end="2025-01-02 10:00", slope=1.0):
    times = pd.date_range(start, end, freq="1min", tz="Asia/Shanghai")
    return pd.DataFrame(
        {
            "symbol": "000852.SH",
            "trading_day": times.strftime("%Y-%m-%d"),
            "market_time_shanghai": times,
            "close": 100.0 + slope * np.arange(len(times)),
            "high_frequency_analysis_eligible": True,
            "causal_flat_fill": False,
            "source_minute_count": 1,
        }
    )


def _states(times, state="Unsafe"):
    values = list(pd.DatetimeIndex(times))
    return pd.DataFrame(
        {
            "symbol": "000852.SH",
            "market_time_shanghai": list(values),
            "state": state,
            "state_available_at": list(values),
        }
    )


def test_state_pool_rejects_future_availability():
    market = _market()
    states = _states(market["market_time_shanghai"])
    states.loc[3, "state_available_at"] = states.loc[3, "market_time_shanghai"] + pd.Timedelta(minutes=1)
    with pytest.raises(StatePoolError, match="later than decision"):
        validate_state_pool(states)


def test_state_pool_rejects_duplicate_timestamp():
    market = _market()
    states = _states(market["market_time_shanghai"])
    states = pd.concat([states, states.iloc[[2]]], ignore_index=True)
    with pytest.raises(StatePoolError, match="duplicate state rows"):
        validate_state_pool(states)


def test_state_pool_rejects_2026():
    times = pd.date_range("2026-01-05 09:30", periods=3, freq="1min", tz="Asia/Shanghai")
    with pytest.raises(StatePoolError, match="2026 rows"):
        validate_state_pool(_states(times))


def test_monotone_path_makes_trend_positive_and_reversion_negative():
    market = _market(slope=1.0)
    states = _states(market["market_time_shanghai"])
    trend = build_frequency_observations(market, states, horizon=5, family="trend")
    reversal = build_frequency_observations(market, states, horizon=5, family="reversion")
    assert len(trend) == 5
    assert (trend["gross_edge_bp"] > 0).all()
    assert (reversal["gross_edge_bp"] < 0).all()
    assert np.allclose(trend["gross_edge_bp"], -reversal["gross_edge_bp"])


def test_missing_physical_minute_is_not_bridged_by_row_position():
    market = _market()
    missing_time = pd.Timestamp("2025-01-02 09:40", tz="Asia/Shanghai")
    market = market.loc[market["market_time_shanghai"].ne(missing_time)].copy()
    states = _states(pd.date_range("2025-01-02 09:30", "2025-01-02 10:00", freq="1min", tz="Asia/Shanghai"))
    obs = build_frequency_observations(market, states, horizon=5, family="trend")
    forbidden = {
        pd.Timestamp("2025-01-02 09:35", tz="Asia/Shanghai"),
        pd.Timestamp("2025-01-02 09:40", tz="Asia/Shanghai"),
        pd.Timestamp("2025-01-02 09:45", tz="Asia/Shanghai"),
    }
    assert forbidden.isdisjoint(set(obs["market_time_shanghai"]))


def test_state_change_closes_and_reopens_router_turnover():
    market = _market(end="2025-01-02 10:10")
    states = _states(market["market_time_shanghai"])
    states.loc[states["market_time_shanghai"] >= pd.Timestamp("2025-01-02 09:50", tz="Asia/Shanghai"), "state"] = "Recovering"
    obs = build_frequency_observations(market, states, horizon=5, family="trend")
    unsafe = obs.loc[obs["state"].eq("Unsafe")]
    recovering = obs.loc[obs["state"].eq("Recovering")]
    assert unsafe["turnover_units"].sum() >= 2.0
    assert recovering["turnover_units"].sum() >= 2.0
    assert obs["state_run_id"].nunique() == 2


def test_summary_uses_actual_turnover_for_break_even_cost():
    market = _market(slope=0.2)
    states = _states(market["market_time_shanghai"])
    obs = build_frequency_observations(market, states, horizon=5, family="trend")
    summary = summarize_observations(obs)
    row = summary.iloc[0]
    expected = obs["gross_edge_bp"].sum() / obs["turnover_units"].sum()
    assert row["break_even_oneway_cost_bp"] == pytest.approx(expected)
    assert row["net_edge_bp_c3"] == pytest.approx(
        (obs["gross_edge_bp"].sum() - 3.0 * obs["turnover_units"].sum()) / len(obs)
    )
