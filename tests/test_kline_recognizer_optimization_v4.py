from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from regime_lab.kline_recognizer_optimization_v4 import (
    CandidateConfig,
    FEATURE_COLUMNS,
    candidate_selection_key,
    fit_diagonal_gaussian_model,
    fit_linear_model,
    frozen_candidate_menu,
    holdout_success,
    select_candidate,
)


def test_candidate_menu_is_frozen_to_thirteen_configs():
    menu = frozen_candidate_menu()
    assert len(menu) == 13
    assert menu[0] == CandidateConfig("rule", 2)
    assert sum(c.family == "linear" for c in menu) == 9
    assert sum(c.family == "diagonal_gaussian" for c in menu) == 3


def test_rule_baseline_cannot_be_retuned():
    with pytest.raises(ValueError):
        CandidateConfig("rule", 1)
    with pytest.raises(ValueError):
        CandidateConfig("rule", 2, 1.0)


def test_feature_surface_contains_no_independent_judge_fields():
    assert len(FEATURE_COLUMNS) == 12
    assert all("independent" not in name for name in FEATURE_COLUMNS)
    assert all("oracle" not in name for name in FEATURE_COLUMNS)
    assert all("future" not in name for name in FEATURE_COLUMNS)


def _separable_four_class_data(seed: int = 7):
    rng = np.random.default_rng(seed)
    centers = np.array(
        [
            [2.5, 2.0],
            [-2.5, -2.0],
            [2.5, -2.0],
            [-2.5, 2.0],
        ]
    )
    X = np.vstack([center + rng.normal(scale=0.25, size=(80, 2)) for center in centers])
    y = np.repeat(np.arange(4), 80)
    return X, y


def test_linear_model_fits_balanced_separable_classes():
    X, y = _separable_four_class_data()
    # Expand to the frozen 12-feature surface with deterministic nuisance columns.
    X12 = np.column_stack([X, np.tile(np.arange(10, dtype=float), (len(X), 1))])
    model = fit_linear_model(X12, y, C=1.0)
    weights = np.asarray(model["weights"], dtype=float)
    assert weights.shape == (4, 13)
    assert np.isfinite(weights).all()


def test_diagonal_gaussian_model_has_all_four_classes():
    X, y = _separable_four_class_data()
    X12 = np.column_stack([X, np.tile(np.arange(10, dtype=float), (len(X), 1))])
    model = fit_diagonal_gaussian_model(X12, y)
    assert len(model["class_means"]) == 4
    assert len(model["class_variances"]) == 4
    assert sum(model["class_priors"]) == pytest.approx(1.0)


def _asset_result(bal: float, macro: float, transition: float, false_day: float):
    return {
        "balanced_accuracy_4state": bal,
        "macro_f1_4state": macro,
        "transition_f1": transition,
        "false_transitions_per_day": false_day,
    }


def test_selection_objective_prioritizes_worst_asset_balanced_accuracy():
    rule = CandidateConfig("rule", 2)
    linear = CandidateConfig("linear", 2, 1.0)
    rule_result = {
        "000852.SH": _asset_result(0.70, 0.90, 0.90, 0.2),
        "000688.SH": _asset_result(0.60, 0.90, 0.90, 0.2),
    }
    linear_result = {
        "000852.SH": _asset_result(0.66, 0.60, 0.40, 0.5),
        "000688.SH": _asset_result(0.65, 0.60, 0.40, 0.5),
    }
    selected, _ = select_candidate([(rule, rule_result), (linear, linear_result)])
    assert selected == linear
    assert candidate_selection_key(linear, linear_result) > candidate_selection_key(rule, rule_result)


def test_deterministic_tie_break_prefers_simpler_family():
    common = {
        "000852.SH": _asset_result(0.70, 0.70, 0.40, 0.4),
        "000688.SH": _asset_result(0.70, 0.70, 0.40, 0.4),
    }
    rule = CandidateConfig("rule", 2)
    linear = CandidateConfig("linear", 1, 0.1)
    selected, _ = select_candidate([(linear, common), (rule, common)])
    assert selected == rule


def test_holdout_success_requires_transition_and_false_alarm_gates():
    baseline = {
        "000852.SH": {"balanced_accuracy_4state": 0.74},
        "000688.SH": {"balanced_accuracy_4state": 0.74},
    }
    optimized = {
        "000852.SH": {
            "balanced_accuracy_4state": 0.75,
            "macro_f1_4state": 0.74,
            "transition_f1": 0.24,
            "false_transitions_per_day": 0.4,
        },
        "000688.SH": {
            "balanced_accuracy_4state": 0.75,
            "macro_f1_4state": 0.74,
            "transition_f1": 0.30,
            "false_transitions_per_day": 0.8,
        },
    }
    result = holdout_success(optimized, baseline)
    assert result["status"] == "recognizer_not_yet_improved"
    assert any("transition_f1" in item for item in result["failures"])
    assert any("false_transitions_per_day" in item for item in result["failures"])
