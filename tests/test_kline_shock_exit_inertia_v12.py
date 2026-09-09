from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_shock_exit_inertia_v12 import (
    ShockExitInertiaCandidate,
    candidate_is_promotable,
    frozen_shock_exit_menu,
    shock_exit_inertia_decode,
)


def _frame(days=("2024-01-02",), bars=8):
    rows = []
    idx = 0
    for day in days:
        base = pd.Timestamp(f"{day} 09:35:00", tz="Asia/Shanghai")
        for i in range(bars):
            rows.append(
                {
                    "idx": idx,
                    "symbol": "000852.SH",
                    "trading_day": day,
                    "market_time_shanghai": base + pd.Timedelta(minutes=5 * i),
                    "recognition_eligible": True,
                }
            )
            idx += 1
    return pd.DataFrame(rows).set_index("idx")


def _probabilities(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def test_frozen_v12_menu_is_exactly_three():
    menu = frozen_shock_exit_menu()
    assert [c.gamma for c in menu] == [0.10, 0.20, 0.30]


def test_stronger_gamma_delays_only_shock_exit():
    frame = _frame(bars=8)
    probs = _probabilities(
        frame,
        [[0.05, 0.05, 0.10, 0.80]] * 4
        + [[0.02, 0.02, 0.53, 0.43]] * 4,
    )
    weak = shock_exit_inertia_decode(frame, probs, ShockExitInertiaCandidate(0.10))
    strong = shock_exit_inertia_decode(frame, probs, ShockExitInertiaCandidate(0.30))
    assert weak.iloc[3] == "Shock"
    assert weak.iloc[-1] == "Range"
    assert strong.iloc[3] == "Shock"
    assert strong.iloc[-1] == "Shock"


def test_gamma_does_not_slow_entry_into_shock():
    frame = _frame(bars=4)
    probs = _probabilities(frame, [[0.05, 0.05, 0.10, 0.80]] * 4)
    a = shock_exit_inertia_decode(frame, probs, ShockExitInertiaCandidate(0.10))
    b = shock_exit_inertia_decode(frame, probs, ShockExitInertiaCandidate(0.30))
    assert a.tolist() == b.tolist()
    assert a.iloc[-1] == "Shock"


def test_decoder_resets_memory_each_day():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=4)
    probs = _probabilities(
        frame,
        [[0.05, 0.05, 0.10, 0.80]] * 4
        + [[0.05, 0.05, 0.80, 0.10]] * 4,
    )
    decoded = shock_exit_inertia_decode(frame, probs, ShockExitInertiaCandidate(0.30))
    day2 = decoded.loc[frame["trading_day"].eq("2024-01-03")]
    assert day2.iloc[-1] == "Range"


def test_decoder_is_prefix_causal():
    frame = _frame(bars=10)
    base_rows = [[0.05, 0.05, 0.10, 0.80]] * 4 + [[0.02, 0.02, 0.53, 0.43]] * 6
    probs_a = _probabilities(frame, base_rows)
    probs_b = probs_a.copy()
    probs_b.iloc[8:] = np.array([[0.80, 0.05, 0.10, 0.05], [0.80, 0.05, 0.10, 0.05]])
    a = shock_exit_inertia_decode(frame, probs_a, ShockExitInertiaCandidate(0.20))
    b = shock_exit_inertia_decode(frame, probs_b, ShockExitInertiaCandidate(0.20))
    assert a.iloc[:8].tolist() == b.iloc[:8].tolist()


def test_promotion_requires_v10_noninferiority_and_material_gain():
    champion = {
        "min_balanced_accuracy": 0.755,
        "min_macro_f1": 0.759,
        "min_transition_f1": 0.198,
        "max_false_transitions_per_day": 1.207,
    }
    good = {
        "min_balanced_accuracy": 0.756,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.210,
        "max_false_transitions_per_day": 1.18,
    }
    too_small = {
        "min_balanced_accuracy": 0.756,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.200,
        "max_false_transitions_per_day": 1.18,
    }
    point_loss = {
        "min_balanced_accuracy": 0.754,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.220,
        "max_false_transitions_per_day": 1.10,
    }
    assert candidate_is_promotable(good, champion)
    assert not candidate_is_promotable(too_small, champion)
    assert not candidate_is_promotable(point_loss, champion)
