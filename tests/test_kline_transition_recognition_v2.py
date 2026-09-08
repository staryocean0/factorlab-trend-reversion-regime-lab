from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from regime_lab.kline_state_recognition import RecognitionConfig
from regime_lab.kline_transition_recognition_v2 import (
    build_v2_state_frame,
    compare_availability_aligned_transitions,
)


def _state_frame(n: int = 20) -> pd.DataFrame:
    times = pd.date_range("2025-01-02 09:30", periods=n, freq="5min", tz="Asia/Shanghai")
    return pd.DataFrame(
        {
            "symbol": "000852.SH",
            "trading_day": "2025-01-02",
            "market_time_shanghai": times,
            "bar_ordinal_day": np.arange(n),
            "recognition_eligible": True,
            "online_state": "Uncertain",
            "oracle_state": "Uncertain",
        }
    )


def test_v2_decoder_carries_confirmed_state_through_uncertain():
    frame = _state_frame(14)
    frame.loc[0:1, "online_state"] = "UpTrend"
    frame.loc[0:10, "oracle_state"] = "UpTrend"
    out, _, _ = build_v2_state_frame(frame)
    assert out.loc[1, "online_decoded_state"] == "UpTrend"
    assert (out.loc[2:10, "online_decoded_state"] == "UpTrend").all()


def test_oracle_target_is_shifted_by_exact_six_eligible_bars():
    frame = _state_frame(16)
    frame.loc[:, "oracle_state"] = "UpTrend"
    frame.loc[:, "online_state"] = "UpTrend"
    out, _, _ = build_v2_state_frame(frame)
    # Oracle becomes confirmed at eligible ordinal 1. Its availability-aligned
    # target therefore first becomes concrete at ordinal 7 (=1+6).
    assert pd.isna(out.loc[5, "oracle_available_state"])
    assert out.loc[6, "oracle_available_state"] == "Uncertain"
    assert out.loc[7, "oracle_available_state"] == "UpTrend"


def test_alignment_uses_eligible_bar_sequence_not_raw_row_distance():
    frame = _state_frame(18)
    frame.loc[:, "oracle_state"] = "UpTrend"
    frame.loc[:, "online_state"] = "UpTrend"
    frame.loc[4, "recognition_eligible"] = False
    out, _, _ = build_v2_state_frame(frame)
    eligible_indices = list(out.index[out["recognition_eligible"]])
    source_idx = eligible_indices[1]
    target_idx = eligible_indices[7]
    assert out.at[source_idx, "oracle_confirmed_center_state"] == "UpTrend"
    assert out.at[target_idx, "oracle_available_state"] == "UpTrend"


def _event(source: str, time: pd.Timestamp, ordinal: int, to_state: str = "DownTrend") -> dict[str, object]:
    return {
        "source": source,
        "symbol": "000852.SH",
        "trading_day": "2025-01-02",
        "from_state": "UpTrend",
        "to_state": to_state,
        "change_start_time": time - pd.Timedelta(minutes=5),
        "event_time": time,
        "bar_ordinal_day": ordinal,
    }


def test_six_bar_structural_delay_is_exact_match_at_oracle_availability():
    frame = _state_frame(20)
    oracle_time = frame.loc[5, "market_time_shanghai"]
    online_time = frame.loc[11, "market_time_shanghai"]
    oracle = pd.DataFrame([_event("oracle", oracle_time, 5)])
    online = pd.DataFrame([_event("online", online_time, 11)])
    _, summary, audit = compare_availability_aligned_transitions(frame, online, oracle)
    assert audit["oracle_availability_lag_bars"] == 6
    assert summary["matched_transition_count"] == 1
    assert summary["transition_precision"] == pytest.approx(1.0)
    assert summary["transition_recall"] == pytest.approx(1.0)
    assert summary["transition_f1"] == pytest.approx(1.0)
    assert summary["median_delay_vs_availability_bars"] == pytest.approx(0.0)
    assert summary["median_delay_vs_center_bars"] == pytest.approx(6.0)


def test_oracle_event_without_same_day_availability_is_excluded():
    frame = _state_frame(12)
    oracle_time = frame.loc[8, "market_time_shanghai"]
    oracle = pd.DataFrame([_event("oracle", oracle_time, 8)])
    online = pd.DataFrame(columns=[
        "source", "symbol", "trading_day", "from_state", "to_state",
        "change_start_time", "event_time", "bar_ordinal_day"
    ])
    _, summary, audit = compare_availability_aligned_transitions(frame, online, oracle)
    assert audit["oracle_events_excluded_unavailable_same_day"] == 1
    assert audit["oracle_events_scored"] == 0
    assert summary["oracle_transition_count"] == 0


def test_non_frozen_alignment_lag_fails_closed():
    frame = _state_frame(16)
    with pytest.raises(ValueError, match="lag must equal"):
        build_v2_state_frame(frame, config=RecognitionConfig(), lag_bars=5)
