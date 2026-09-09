from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_persistence_prior_v13 import (
    PersistencePriorCandidate,
    candidate_is_promotable,
    frozen_persistence_menu,
    one_step_persistence_probabilities,
)


def _frame(days=("2024-01-02",), bars=3):
    rows = []
    idx = 0
    for day in days:
        base = pd.Timestamp(f"{day} 09:35:00", tz="Asia/Shanghai")
        for i in range(bars):
            rows.append({
                "idx": idx,
                "symbol": "000852.SH",
                "trading_day": day,
                "market_time_shanghai": base + pd.Timedelta(minutes=5 * i),
            })
            idx += 1
    return pd.DataFrame(rows).set_index("idx")


def _probs(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def _markov():
    return {
        "transition_matrix": [
            [0.90, 0.03, 0.05, 0.02],
            [0.03, 0.90, 0.05, 0.02],
            [0.08, 0.08, 0.80, 0.04],
            [0.04, 0.04, 0.12, 0.80],
        ]
    }


def test_frozen_v13_menu_is_exactly_three():
    assert [x.rho for x in frozen_persistence_menu()] == [0.05, 0.10, 0.15]


def test_first_bar_each_day_is_exact_v10_base():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=2)
    base = _probs(frame, [
        [0.7, 0.1, 0.1, 0.1], [0.6, 0.1, 0.2, 0.1],
        [0.1, 0.7, 0.1, 0.1], [0.1, 0.6, 0.2, 0.1],
    ])
    out = one_step_persistence_probabilities(frame, base, _markov(), PersistencePriorCandidate(0.10))
    for day in ("2024-01-02", "2024-01-03"):
        idx = frame.index[frame["trading_day"].eq(day)][0]
        np.testing.assert_allclose(out.loc[idx].to_numpy(float), base.loc[idx].to_numpy(float))


def test_prior_is_normalized_and_weakly_favors_persistent_previous_state():
    frame = _frame(bars=2)
    base = _probs(frame, [
        [0.85, 0.05, 0.05, 0.05],
        [0.45, 0.05, 0.45, 0.05],
    ])
    out = one_step_persistence_probabilities(frame, base, _markov(), PersistencePriorCandidate(0.15))
    assert np.isclose(out.iloc[1].sum(), 1.0)
    assert out.iloc[1]["UpTrend"] > base.iloc[1]["UpTrend"]
    assert out.iloc[1]["Range"] < base.iloc[1]["Range"]


def test_prior_is_one_step_not_recursive():
    frame = _frame(bars=3)
    a = _probs(frame, [
        [0.90, 0.03, 0.05, 0.02],
        [0.10, 0.10, 0.75, 0.05],
        [0.20, 0.10, 0.65, 0.05],
    ])
    b = a.copy()
    b.iloc[0] = [0.03, 0.90, 0.05, 0.02]
    ca = one_step_persistence_probabilities(frame, a, _markov(), PersistencePriorCandidate(0.15))
    cb = one_step_persistence_probabilities(frame, b, _markov(), PersistencePriorCandidate(0.15))
    # Bar 2 may differ because bar 1 differs, but bar 3 depends only on identical base bar 2.
    assert not np.allclose(ca.iloc[1].to_numpy(float), cb.iloc[1].to_numpy(float))
    np.testing.assert_allclose(ca.iloc[2].to_numpy(float), cb.iloc[2].to_numpy(float))


def test_missing_base_breaks_prior_chain_instead_of_carrying_memory():
    frame = _frame(bars=3)
    base = _probs(frame, [
        [0.85, 0.05, 0.05, 0.05],
        [np.nan, np.nan, np.nan, np.nan],
        [0.20, 0.10, 0.65, 0.05],
    ])
    out = one_step_persistence_probabilities(frame, base, _markov(), PersistencePriorCandidate(0.15))
    assert out.iloc[1].isna().all()
    np.testing.assert_allclose(out.iloc[2].to_numpy(float), base.iloc[2].to_numpy(float))


def test_promotion_requires_v10_noninferiority_and_material_gain():
    champion = {
        "min_balanced_accuracy": 0.755,
        "min_macro_f1": 0.759,
        "min_transition_f1": 0.198,
        "max_false_transitions_per_day": 1.207,
    }
    good = {
        "min_balanced_accuracy": 0.766,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.199,
        "max_false_transitions_per_day": 1.20,
    }
    too_small = {
        "min_balanced_accuracy": 0.756,
        "min_macro_f1": 0.760,
        "min_transition_f1": 0.200,
        "max_false_transitions_per_day": 1.18,
    }
    trans_loss = {
        "min_balanced_accuracy": 0.780,
        "min_macro_f1": 0.780,
        "min_transition_f1": 0.197,
        "max_false_transitions_per_day": 1.00,
    }
    assert candidate_is_promotable(good, champion)
    assert not candidate_is_promotable(too_small, champion)
    assert not candidate_is_promotable(trans_loss, champion)
