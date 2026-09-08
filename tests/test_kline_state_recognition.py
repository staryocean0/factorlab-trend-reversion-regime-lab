from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from regime_lab.kline_state_recognition import (
    RecognitionConfig,
    build_causal_features,
    classify_state,
    compare_transition_events,
    confirmed_states_and_events,
    prepare_market_frame,
    score_recognition,
)


def _one_day_market() -> pd.DataFrame:
    am = pd.date_range("2025-01-02 09:30", "2025-01-02 11:30", freq="5min", tz="Asia/Shanghai")
    pm = pd.date_range("2025-01-02 13:00", "2025-01-02 15:00", freq="5min", tz="Asia/Shanghai")
    times = am.append(pm)
    close = 100.0 + np.linspace(0.0, 2.0, len(times))
    return pd.DataFrame(
        {
            "symbol": "000852.SH",
            "trading_day": times.strftime("%Y-%m-%d"),
            "market_time_shanghai": times,
            "open": close - 0.02,
            "high": close + 0.05,
            "low": close - 0.05,
            "close": close,
            "high_frequency_analysis_eligible": True,
            "causal_flat_fill": False,
            "source_minute_count": 5,
        }
    )


def test_frozen_state_rule_distinguishes_four_concrete_states():
    cfg = RecognitionConfig()
    assert classify_state(
        efficiency_short=0.4,
        efficiency_primary=0.5,
        bdci=70.0,
        dii=1.4,
        volatility_rank=0.5,
        abs_return_rank=0.5,
        config=cfg,
    ) == "UpTrend"
    assert classify_state(
        efficiency_short=-0.4,
        efficiency_primary=-0.5,
        bdci=70.0,
        dii=-1.4,
        volatility_rank=0.5,
        abs_return_rank=0.5,
        config=cfg,
    ) == "DownTrend"
    assert classify_state(
        efficiency_short=0.05,
        efficiency_primary=0.10,
        bdci=25.0,
        dii=0.20,
        volatility_rank=0.5,
        abs_return_rank=0.5,
        config=cfg,
    ) == "Range"
    assert classify_state(
        efficiency_short=0.4,
        efficiency_primary=0.5,
        bdci=70.0,
        dii=1.4,
        volatility_rank=0.91,
        abs_return_rank=0.5,
        config=cfg,
    ) == "Shock"


def test_missing_rank_context_abstains_instead_of_guessing():
    assert classify_state(
        efficiency_short=0.5,
        efficiency_primary=0.6,
        bdci=80.0,
        dii=2.0,
        volatility_rank=math.nan,
        abs_return_rank=0.3,
    ) == "Uncertain"


def test_online_features_are_prefix_only_when_future_bars_change():
    market = _one_day_market()
    prepared = prepare_market_frame(market)
    before = build_causal_features(prepared)

    changed = market.copy()
    future = changed.index >= 40
    changed.loc[future, "open"] += 20.0
    changed.loc[future, "high"] += 20.0
    changed.loc[future, "low"] += 20.0
    changed.loc[future, "close"] += 20.0
    after = build_causal_features(prepare_market_frame(changed))

    cutoff = 35
    columns = [
        "signed_efficiency_6",
        "signed_efficiency_24",
        "bdci_24",
        "dii_24",
        "realized_volatility_24",
        "body_to_range_ratio_6",
        "wick_imbalance_6",
        "close_location_value_6",
    ]
    pd.testing.assert_frame_equal(
        before.loc[:cutoff, columns],
        after.loc[:cutoff, columns],
        check_dtype=False,
    )


def test_2026_market_rows_fail_closed():
    market = _one_day_market()
    market["market_time_shanghai"] = market["market_time_shanghai"] + pd.DateOffset(years=1)
    market["trading_day"] = pd.to_datetime(market["market_time_shanghai"]).dt.strftime("%Y-%m-%d")
    with pytest.raises(ValueError, match="2026 rows"):
        prepare_market_frame(market)


def test_two_bar_confirmation_creates_one_transition():
    times = pd.date_range("2025-01-02 09:30", periods=8, freq="5min", tz="Asia/Shanghai")
    frame = pd.DataFrame(
        {
            "symbol": "000852.SH",
            "trading_day": "2025-01-02",
            "market_time_shanghai": times,
            "bar_ordinal_day": np.arange(len(times)),
            "label": [
                "UpTrend",
                "UpTrend",
                "Uncertain",
                "Range",
                "Range",
                "Range",
                "DownTrend",
                "DownTrend",
            ],
        }
    )
    confirmed, events = confirmed_states_and_events(frame, label_column="label", source="test")
    assert confirmed.iloc[1] == "UpTrend"
    assert list(events["to_state"]) == ["Range", "DownTrend"]
    assert list(events["bar_ordinal_day"]) == [4, 7]


def _event(source: str, ordinal: int, to_state: str) -> dict[str, object]:
    return {
        "source": source,
        "symbol": "000852.SH",
        "trading_day": "2025-01-02",
        "from_state": "Range",
        "to_state": to_state,
        "change_start_time": pd.Timestamp("2025-01-02 10:00", tz="Asia/Shanghai"),
        "event_time": pd.Timestamp("2025-01-02 10:05", tz="Asia/Shanghai"),
        "bar_ordinal_day": ordinal,
    }


def test_transition_matching_is_destination_specific_and_within_tolerance():
    online = pd.DataFrame([_event("online", 12, "UpTrend"), _event("online", 30, "DownTrend")])
    oracle = pd.DataFrame([_event("oracle", 10, "UpTrend"), _event("oracle", 20, "DownTrend")])
    _, metrics = compare_transition_events(online, oracle, tolerance_bars=3)
    assert metrics["matched_transition_count"] == 1
    assert metrics["transition_precision"] == pytest.approx(0.5)
    assert metrics["transition_recall"] == pytest.approx(0.5)
    assert metrics["transition_f1"] == pytest.approx(0.5)


def test_zero_matches_produce_zero_transition_f1_not_nan():
    online = pd.DataFrame([_event("online", 30, "UpTrend")])
    oracle = pd.DataFrame([_event("oracle", 10, "UpTrend")])
    _, metrics = compare_transition_events(online, oracle, tolerance_bars=3)
    assert metrics["transition_precision"] == 0.0
    assert metrics["transition_recall"] == 0.0
    assert metrics["transition_f1"] == 0.0


def test_abstention_counts_as_recognition_miss():
    times = pd.date_range("2025-01-02 09:30", periods=8, freq="5min", tz="Asia/Shanghai")
    oracle = ["UpTrend", "DownTrend", "Range", "Shock"] * 2
    online = ["UpTrend", "DownTrend", "Range", "Uncertain"] * 2
    frame = pd.DataFrame(
        {
            "symbol": "000852.SH",
            "trading_day": "2025-01-02",
            "market_time_shanghai": times,
            "bar_ordinal_day": np.arange(len(times)),
            "oracle_state": oracle,
            "online_state": online,
        }
    )
    summary, _, per_state, _, _ = score_recognition(frame)
    assert summary["online_concrete_coverage"] == pytest.approx(0.75)
    assert summary["exact_accuracy_including_abstention"] == pytest.approx(0.75)
    assert summary["balanced_accuracy_4state"] == pytest.approx(0.75)
    shock = per_state.loc[per_state["state"].eq("Shock")].iloc[0]
    assert shock["recall"] == 0.0
    assert shock["f1"] == 0.0
