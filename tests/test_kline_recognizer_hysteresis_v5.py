from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from regime_lab.kline_recognizer_hysteresis_v5 import (
    HysteresisPolicy,
    V4_POLICY,
    frozen_hysteresis_menu,
    hysteresis_decode,
    linear_probabilities,
    select_hysteresis_policy,
)
from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES, FEATURE_COLUMNS


def _frame(days=("2024-01-02",), bars=6):
    rows = []
    for day in days:
        times = pd.date_range(f"{day} 09:30", periods=bars, freq="5min", tz="Asia/Shanghai")
        for ts in times:
            row = {
                "symbol": "000852.SH",
                "trading_day": day,
                "market_time_shanghai": ts,
                "recognition_eligible": True,
            }
            row.update({feature: 0.0 for feature in FEATURE_COLUMNS})
            rows.append(row)
    return pd.DataFrame(rows)


def _probabilities(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def test_frozen_menu_has_exactly_60_policies_and_v4_baseline():
    menu = frozen_hysteresis_menu()
    assert len(menu) == 60
    assert len(set(menu)) == 60
    assert V4_POLICY in menu


def test_policy_rejects_values_outside_frozen_grid():
    with pytest.raises(ValueError):
        HysteresisPolicy(0.07, 0.45, 3)
    with pytest.raises(ValueError):
        HysteresisPolicy(0.10, 0.50, 3)
    with pytest.raises(ValueError):
        HysteresisPolicy(0.10, 0.45, 5)


def test_linear_probabilities_are_normalized():
    frame = _frame(bars=3)
    d = len(FEATURE_COLUMNS)
    model = {
        "family": "linear",
        "C": 1.0,
        "mean": [0.0] * d,
        "scale": [1.0] * d,
        "weights": [[0.0] * (d + 1) for _ in CLASS_NAMES],
    }
    probs = linear_probabilities(frame, model)
    assert np.allclose(probs.sum(axis=1), 1.0)
    assert np.allclose(probs.to_numpy(), 0.25)


def test_hysteresis_holds_current_state_when_margin_is_not_met():
    frame = _frame(bars=6)
    # Enter UpTrend in two bars. Then Range is top, but only by 0.04 < 0.10 margin.
    probs = _probabilities(
        frame,
        [
            [0.70, 0.10, 0.10, 0.10],
            [0.72, 0.08, 0.10, 0.10],
            [0.43, 0.05, 0.47, 0.05],
            [0.42, 0.05, 0.46, 0.07],
            [0.41, 0.05, 0.45, 0.09],
            [0.44, 0.05, 0.46, 0.05],
        ],
    )
    policy = HysteresisPolicy(0.10, 0.45, 2)
    decoded = hysteresis_decode(frame, probs, policy)
    assert decoded.iloc[0] == "Uncertain"
    assert decoded.iloc[1] == "UpTrend"
    assert decoded.iloc[-1] == "UpTrend"


def test_hysteresis_switches_only_after_qualifying_consecutive_bars():
    frame = _frame(bars=6)
    probs = _probabilities(
        frame,
        [
            [0.70, 0.10, 0.10, 0.10],
            [0.72, 0.08, 0.10, 0.10],
            [0.74, 0.06, 0.10, 0.10],
            [0.28, 0.05, 0.62, 0.05],
            [0.25, 0.05, 0.65, 0.05],
            [0.20, 0.05, 0.70, 0.05],
        ],
    )
    policy = HysteresisPolicy(0.10, 0.55, 3)
    decoded = hysteresis_decode(frame, probs, policy)
    assert decoded.iloc[1] == "Uncertain"
    assert decoded.iloc[2] == "UpTrend"
    assert decoded.iloc[3] == "UpTrend"
    assert decoded.iloc[4] == "UpTrend"
    assert decoded.iloc[5] == "Range"


def test_hysteresis_resets_state_at_new_trading_day():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=2)
    probs = _probabilities(
        frame,
        [
            [0.8, 0.1, 0.05, 0.05],
            [0.8, 0.1, 0.05, 0.05],
            [0.1, 0.8, 0.05, 0.05],
            [0.1, 0.8, 0.05, 0.05],
        ],
    )
    decoded = hysteresis_decode(frame, probs, HysteresisPolicy(0.0, 0.0, 2))
    assert decoded.iloc[1] == "UpTrend"
    assert decoded.iloc[2] == "Uncertain"
    assert decoded.iloc[3] == "DownTrend"


def test_selector_uses_point_floors_and_falls_back_to_v4_if_none_eligible():
    good = HysteresisPolicy(0.10, 0.45, 3)
    rows = [
        (
            V4_POLICY,
            {
                "min_balanced_accuracy": 0.74,
                "min_macro_f1": 0.71,
                "min_transition_f1": 0.20,
                "max_false_transitions_per_day": 0.8,
            },
        ),
        (
            good,
            {
                "min_balanced_accuracy": 0.73,
                "min_macro_f1": 0.80,
                "min_transition_f1": 0.40,
                "max_false_transitions_per_day": 0.5,
            },
        ),
    ]
    selected, _, eligible = select_hysteresis_policy(rows)
    assert selected == V4_POLICY
    assert not eligible


def test_selector_prefers_transition_f1_after_point_floors():
    a = HysteresisPolicy(0.05, 0.45, 3)
    b = HysteresisPolicy(0.10, 0.55, 3)
    common = {"min_balanced_accuracy": 0.80, "min_macro_f1": 0.78}
    rows = [
        (a, {**common, "min_transition_f1": 0.30, "max_false_transitions_per_day": 0.5}),
        (b, {**common, "min_transition_f1": 0.35, "max_false_transitions_per_day": 0.7}),
    ]
    selected, _, eligible = select_hysteresis_policy(rows)
    assert eligible
    assert selected == b
