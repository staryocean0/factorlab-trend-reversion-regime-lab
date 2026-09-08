from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_markov_filter_v7 import (
    MarkovCandidate,
    fit_markov_state_model,
    frozen_markov_menu,
    markov_filter_decode,
    markov_promotable,
    select_markov_candidate,
    sharpen_transition_matrix,
)


def _frame(days=("2024-01-02",), bars=6):
    rows = []
    for day in days:
        times = pd.date_range(f"{day} 09:30", periods=bars, freq="5min", tz="Asia/Shanghai")
        for ordinal, ts in enumerate(times):
            rows.append(
                {
                    "symbol": "000852.SH",
                    "trading_day": day,
                    "market_time_shanghai": ts,
                    "recognition_eligible": True,
                    "independent_v3_score_eligible": True,
                    "independent_judge_available_state": "UpTrend",
                    "eligible_ordinal_day_v3": ordinal,
                }
            )
    return pd.DataFrame(rows)


def _probabilities(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def test_frozen_markov_menu_has_exactly_12_candidates():
    menu = frozen_markov_menu()
    assert len(menu) == 12
    assert len({c.candidate_id for c in menu}) == 12


def test_markov_fit_does_not_count_overnight_transition():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=2)
    frame.loc[0:1, "independent_judge_available_state"] = ["UpTrend", "Range"]
    frame.loc[2:3, "independent_judge_available_state"] = ["Shock", "DownTrend"]
    model = fit_markov_state_model({"000852.SH": frame}, start=None, end="2024-12-31")
    counts = np.asarray(model["transition_counts"], dtype=float)
    up = CLASS_NAMES.index("UpTrend")
    rng = CLASS_NAMES.index("Range")
    sh = CLASS_NAMES.index("Shock")
    down = CLASS_NAMES.index("DownTrend")
    # pseudocount 1 + one within-day observed transition
    assert counts[up, rng] == 2.0
    assert counts[sh, down] == 2.0
    # Range -> Shock is overnight and must remain pseudocount only.
    assert counts[rng, sh] == 1.0
    assert model["observed_transition_pairs"] == 2


def test_markov_fit_skips_nonconsecutive_eligible_ordinals():
    frame = _frame(bars=3)
    frame["eligible_ordinal_day_v3"] = [0, 2, 3]
    frame["independent_judge_available_state"] = ["UpTrend", "Range", "Shock"]
    model = fit_markov_state_model({"000852.SH": frame}, start=None, end="2024-12-31")
    counts = np.asarray(model["transition_counts"], dtype=float)
    up = CLASS_NAMES.index("UpTrend")
    rng = CLASS_NAMES.index("Range")
    sh = CLASS_NAMES.index("Shock")
    assert counts[up, rng] == 1.0
    assert counts[rng, sh] == 2.0
    assert model["observed_transition_pairs"] == 1


def test_sharpening_preserves_rows_and_strengthens_dominant_transition():
    matrix = np.array(
        [
            [0.8, 0.1, 0.05, 0.05],
            [0.1, 0.8, 0.05, 0.05],
            [0.1, 0.1, 0.7, 0.1],
            [0.1, 0.1, 0.1, 0.7],
        ]
    )
    sharp = sharpen_transition_matrix(matrix, 2.0)
    assert np.allclose(sharp.sum(axis=1), 1.0)
    assert sharp[0, 0] > matrix[0, 0]


def test_markov_filter_is_prefix_causal():
    frame = _frame(bars=6)
    model = {
        "transition_matrix": np.array(
            [
                [0.9, 0.03, 0.04, 0.03],
                [0.03, 0.9, 0.04, 0.03],
                [0.04, 0.04, 0.88, 0.04],
                [0.04, 0.04, 0.04, 0.88],
            ]
        ).tolist(),
        "prior": [0.25, 0.25, 0.25, 0.25],
    }
    rows = [
        [0.70, 0.10, 0.15, 0.05],
        [0.65, 0.10, 0.20, 0.05],
        [0.55, 0.10, 0.30, 0.05],
        [0.45, 0.10, 0.40, 0.05],
        [0.30, 0.10, 0.55, 0.05],
        [0.20, 0.10, 0.65, 0.05],
    ]
    probs = _probabilities(frame, rows)
    candidate = MarkovCandidate(2.0, 1.0)
    original = markov_filter_decode(frame, probs, model, candidate)
    changed = probs.copy()
    changed.iloc[-1] = [0.01, 0.01, 0.01, 0.97]
    modified = markov_filter_decode(frame, changed, model, candidate)
    assert original.iloc[:-1].tolist() == modified.iloc[:-1].tolist()


def test_markov_filter_resets_each_day():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=2)
    model = {
        "transition_matrix": np.eye(4) * 0.97 + (np.ones((4, 4)) - np.eye(4)) * 0.01,
        "prior": [0.25, 0.25, 0.25, 0.25],
    }
    model["transition_matrix"] = np.asarray(model["transition_matrix"]).tolist()
    probs = _probabilities(
        frame,
        [
            [0.9, 0.03, 0.04, 0.03],
            [0.9, 0.03, 0.04, 0.03],
            [0.03, 0.9, 0.04, 0.03],
            [0.03, 0.9, 0.04, 0.03],
        ],
    )
    decoded = markov_filter_decode(frame, probs, model, MarkovCandidate(2.0, 2.0))
    assert decoded.iloc[1] == "UpTrend"
    assert decoded.iloc[2] == "DownTrend"


def test_markov_promotion_requires_no_worse_than_v5_and_material_gain():
    baseline = {
        "min_balanced_accuracy": 0.75,
        "min_macro_f1": 0.75,
        "min_transition_f1": 0.18,
        "max_false_transitions_per_day": 1.20,
    }
    not_material = {
        "min_balanced_accuracy": 0.80,
        "min_macro_f1": 0.80,
        "min_transition_f1": 0.185,
        "max_false_transitions_per_day": 1.18,
    }
    material = {
        "min_balanced_accuracy": 0.80,
        "min_macro_f1": 0.80,
        "min_transition_f1": 0.195,
        "max_false_transitions_per_day": 1.18,
    }
    assert not markov_promotable(not_material, baseline)
    assert markov_promotable(material, baseline)


def test_selector_returns_none_when_no_markov_candidate_beats_v5():
    baseline = {
        "min_balanced_accuracy": 0.76,
        "min_macro_f1": 0.75,
        "min_transition_f1": 0.20,
        "max_false_transitions_per_day": 1.0,
    }
    c = MarkovCandidate(1.0, 1.0)
    aggregate = {
        "min_balanced_accuracy": 0.80,
        "min_macro_f1": 0.79,
        "min_transition_f1": 0.19,
        "max_false_transitions_per_day": 0.9,
    }
    selected, selected_agg, best, best_agg = select_markov_candidate([(c, aggregate)], baseline)
    assert selected is None
    assert selected_agg is None
    assert best == c
    assert best_agg == aggregate
