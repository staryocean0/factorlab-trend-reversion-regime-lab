from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_temporal_blend_v10 import (
    TemporalBlendCandidate,
    blend_probabilities,
    candidate_is_promotable,
    frozen_blend_menu,
    safety_veto_2025,
    select_blend_candidate,
)


def _probs(rows):
    return pd.DataFrame(rows, columns=CLASS_NAMES, dtype=float)


def test_frozen_v10_menu_is_exactly_six():
    menu = frozen_blend_menu()
    assert len(menu) == 6
    assert {(c.horizon, c.alpha) for c in menu} == {
        (3, 0.10), (3, 0.20), (3, 0.30),
        (6, 0.10), (6, 0.20), (6, 0.30),
    }


def test_temporal_absence_falls_back_exactly_to_primary():
    primary = _probs([[0.7, 0.1, 0.1, 0.1], [0.2, 0.2, 0.5, 0.1]])
    temporal = _probs([[np.nan] * 4, [0.1, 0.1, 0.7, 0.1]])
    blended = blend_probabilities(primary, temporal, alpha=0.2)
    np.testing.assert_allclose(blended.iloc[0].to_numpy(), primary.iloc[0].to_numpy())
    assert np.isclose(blended.iloc[1].sum(), 1.0)


def test_auxiliary_cannot_create_prediction_without_primary():
    primary = _probs([[np.nan] * 4])
    temporal = _probs([[0.1, 0.1, 0.7, 0.1]])
    blended = blend_probabilities(primary, temporal, alpha=0.2)
    assert blended.iloc[0].isna().all()


def test_blend_is_normalized_and_between_competing_heads():
    primary = _probs([[0.8, 0.1, 0.05, 0.05]])
    temporal = _probs([[0.2, 0.1, 0.65, 0.05]])
    blended = blend_probabilities(primary, temporal, alpha=0.2)
    assert np.isclose(blended.iloc[0].sum(), 1.0)
    assert temporal.iloc[0]["UpTrend"] < blended.iloc[0]["UpTrend"] < primary.iloc[0]["UpTrend"]
    assert primary.iloc[0]["Range"] < blended.iloc[0]["Range"] < temporal.iloc[0]["Range"]


def test_promotion_requires_noninferiority_and_material_gain():
    champion = {
        "min_balanced_accuracy": 0.754,
        "min_macro_f1": 0.756,
        "min_transition_f1": 0.179,
        "max_false_transitions_per_day": 1.24,
    }
    good = {
        "min_balanced_accuracy": 0.755,
        "min_macro_f1": 0.757,
        "min_transition_f1": 0.191,
        "max_false_transitions_per_day": 1.20,
    }
    no_material = {
        "min_balanced_accuracy": 0.755,
        "min_macro_f1": 0.757,
        "min_transition_f1": 0.180,
        "max_false_transitions_per_day": 1.23,
    }
    point_loss = {
        "min_balanced_accuracy": 0.753,
        "min_macro_f1": 0.757,
        "min_transition_f1": 0.210,
        "max_false_transitions_per_day": 1.00,
    }
    assert candidate_is_promotable(good, champion)
    assert not candidate_is_promotable(no_material, champion)
    assert not candidate_is_promotable(point_loss, champion)


def test_selection_prefers_transition_then_false_transition_control():
    champion = {
        "min_balanced_accuracy": 0.75,
        "min_macro_f1": 0.75,
        "min_transition_f1": 0.18,
        "max_false_transitions_per_day": 1.24,
    }
    a = TemporalBlendCandidate(3, 0.10)
    b = TemporalBlendCandidate(6, 0.20)
    agg_a = {
        "min_balanced_accuracy": 0.76,
        "min_macro_f1": 0.76,
        "min_transition_f1": 0.20,
        "max_false_transitions_per_day": 1.10,
    }
    agg_b = {
        "min_balanced_accuracy": 0.76,
        "min_macro_f1": 0.76,
        "min_transition_f1": 0.21,
        "max_false_transitions_per_day": 1.15,
    }
    selected, _ = select_blend_candidate([(a, agg_a), (b, agg_b)], champion)
    assert selected == b


def test_2025_safety_veto_is_tolerance_based():
    baseline = {
        "000852.SH": {
            "balanced_accuracy_4state": 0.82,
            "macro_f1_4state": 0.81,
            "transition_f1": 0.20,
            "false_transitions_per_day": 1.10,
        }
    }
    safe = {
        "000852.SH": {
            "balanced_accuracy_4state": 0.811,
            "macro_f1_4state": 0.801,
            "transition_f1": 0.191,
            "false_transitions_per_day": 1.149,
        }
    }
    unsafe = {
        "000852.SH": {
            "balanced_accuracy_4state": 0.80,
            "macro_f1_4state": 0.81,
            "transition_f1": 0.20,
            "false_transitions_per_day": 1.10,
        }
    }
    assert not safety_veto_2025(safe, baseline)["veto"]
    assert safety_veto_2025(unsafe, baseline)["veto"]
