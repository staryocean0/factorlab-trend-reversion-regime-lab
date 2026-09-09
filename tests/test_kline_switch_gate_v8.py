from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_switch_gate_v8 import (
    SWITCH_FEATURE_COLUMNS,
    SwitchGateCandidate,
    build_switch_training_rows,
    candidate_promotable,
    fit_switch_gate,
    frozen_switch_gate_menu,
    select_switch_gate_candidate,
    switch_gate_decode,
    switch_gate_probabilities,
)


def _frame(days=("2024-01-02",), bars=6):
    rows = []
    run_id = 0
    for day in days:
        times = pd.date_range(f"{day} 09:30", periods=bars, freq="5min", tz="Asia/Shanghai")
        for ts in times:
            rows.append(
                {
                    "symbol": "000852.SH",
                    "trading_day": day,
                    "market_time_shanghai": ts,
                    "recognition_eligible": True,
                    "contiguous_run_id": run_id,
                    "independent_v3_score_eligible": True,
                    "independent_judge_available_state": "UpTrend",
                }
            )
        run_id += 1
    return pd.DataFrame(rows)


def _probabilities(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def test_frozen_switch_gate_menu_has_exactly_18_candidates():
    menu = frozen_switch_gate_menu()
    assert len(menu) == 18
    assert len(set(menu)) == 18


def test_switch_gate_decoder_requires_threshold_and_confirmation():
    frame = _frame(bars=6)
    probs = _probabilities(
        frame,
        [
            [0.80, 0.05, 0.10, 0.05],
            [0.82, 0.03, 0.10, 0.05],
            [0.20, 0.05, 0.70, 0.05],
            [0.18, 0.05, 0.72, 0.05],
            [0.15, 0.05, 0.75, 0.05],
            [0.10, 0.05, 0.80, 0.05],
        ],
    )
    gate = pd.Series([np.nan, np.nan, 0.60, 0.40, 0.70, 0.80], index=frame.index)
    candidate = SwitchGateCandidate(1.0, 0.50, 2)
    decoded = switch_gate_decode(frame, probs, gate, candidate)
    assert decoded.iloc[0] == "Uncertain"
    assert decoded.iloc[1] == "UpTrend"
    # qualifying count at bar 2 is reset by bar 3, then bars 4+5 switch to Range
    assert decoded.iloc[4] == "UpTrend"
    assert decoded.iloc[5] == "Range"


def test_switch_gate_decoder_resets_daily_memory():
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
    gate = pd.Series(1.0, index=frame.index)
    decoded = switch_gate_decode(frame, probs, gate, SwitchGateCandidate(1.0, 0.50, 1))
    assert decoded.iloc[1] == "UpTrend"
    assert decoded.iloc[2] == "Uncertain"
    assert decoded.iloc[3] == "DownTrend"


def test_switch_training_target_does_not_cross_days_or_gaps():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=3)
    # Day 1 has one genuine within-day switch on the third bar.
    frame.loc[2, "independent_judge_available_state"] = "Range"
    # Day 2 starts in Range; this must not become an overnight switch target.
    frame.loc[3:, "independent_judge_available_state"] = "Range"
    features = pd.DataFrame(0.0, index=frame.index, columns=SWITCH_FEATURE_COLUMNS)
    X, y = build_switch_training_rows(frame, features, start=None, end="2024-12-31")
    assert len(X) == 4  # two adjacent pairs per day
    assert int(y.sum()) == 1


def test_binary_gate_fit_returns_finite_probabilities():
    X = np.array(
        [
            [-2.0, 0.0],
            [-1.0, 0.2],
            [-0.5, -0.1],
            [0.5, 0.1],
            [1.0, -0.2],
            [2.0, 0.0],
        ]
    )
    y = np.array([0, 0, 0, 1, 1, 1])
    model = fit_switch_gate(X, y, C_gate=1.0)
    feature_frame = pd.DataFrame(0.0, index=range(2), columns=SWITCH_FEATURE_COLUMNS)
    # Match the synthetic model dimension for this isolated probability test.
    model = {
        **model,
        "mean": [0.0] * len(SWITCH_FEATURE_COLUMNS),
        "scale": [1.0] * len(SWITCH_FEATURE_COLUMNS),
        "weights": [0.0] * (len(SWITCH_FEATURE_COLUMNS) + 1),
    }
    probs = switch_gate_probabilities(feature_frame, model)
    assert np.all(np.isfinite(probs))
    assert np.allclose(probs.to_numpy(), 0.5)


def test_promotion_gate_rejects_better_accuracy_but_worse_transitions():
    v5 = {
        "min_transition_f1": 0.179,
        "max_false_transitions_per_day": 1.240,
        "min_balanced_accuracy": 0.754,
        "min_macro_f1": 0.756,
    }
    candidate = {
        "min_transition_f1": 0.160,
        "max_false_transitions_per_day": 1.000,
        "min_balanced_accuracy": 0.820,
        "min_macro_f1": 0.810,
    }
    assert not candidate_promotable(candidate, v5)


def test_selector_returns_none_when_no_candidate_beats_v5():
    v5 = {
        "min_transition_f1": 0.179,
        "max_false_transitions_per_day": 1.240,
        "min_balanced_accuracy": 0.754,
        "min_macro_f1": 0.756,
    }
    c = SwitchGateCandidate(1.0, 0.50, 1)
    rows = [
        (
            c,
            {
                "min_transition_f1": 0.180,
                "max_false_transitions_per_day": 1.235,
                "min_balanced_accuracy": 0.800,
                "min_macro_f1": 0.790,
            },
        )
    ]
    selected, aggregate = select_switch_gate_candidate(rows, v5)
    assert selected is None
    assert aggregate is None
