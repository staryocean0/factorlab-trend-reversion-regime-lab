from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import FEATURE_COLUMNS
from regime_lab.kline_temporal_context_v9 import (
    TemporalContextCandidate,
    build_temporal_context,
    candidate_is_promotable,
    frozen_temporal_menu,
    safety_veto_2025,
    select_temporal_candidate,
    temporal_feature_columns,
)


def _frame(days=("2024-01-02",), bars=8) -> pd.DataFrame:
    rows = []
    for day in days:
        base = pd.Timestamp(f"{day} 09:30:00", tz="Asia/Shanghai")
        for i in range(bars):
            row = {
                "symbol": "000852.SH",
                "trading_day": day,
                "contiguous_run_id": f"{day}-am",
                "market_time_shanghai": base + pd.Timedelta(minutes=5 * i),
                "recognition_eligible": True,
                "independent_v3_score_eligible": True,
                "independent_judge_available_state": "UpTrend",
            }
            for j, col in enumerate(FEATURE_COLUMNS):
                row[col] = float(i + j / 100.0)
            rows.append(row)
    return pd.DataFrame(rows)


def _champion() -> dict[str, float]:
    return {
        "min_balanced_accuracy": 0.7536614040741304,
        "min_macro_f1": 0.7562810194148302,
        "min_transition_f1": 0.17902813299232734,
        "max_false_transitions_per_day": 1.2396694214876034,
    }


def test_frozen_v9_menu_is_exactly_six():
    menu = frozen_temporal_menu()
    assert len(menu) == 6
    assert {(x.horizon, x.C) for x in menu} == {
        (h, C) for h in (3, 6) for C in (0.1, 1.0, 10.0)
    }
    assert all(len(temporal_feature_columns(x.horizon)) == 48 for x in menu)


def test_temporal_context_is_prefix_causal():
    frame = _frame(bars=8)
    original = build_temporal_context(frame, horizon=3)
    changed = frame.copy()
    for col in FEATURE_COLUMNS:
        changed.loc[7, col] = 1_000_000.0
    altered = build_temporal_context(changed, horizon=3)
    pd.testing.assert_frame_equal(original.loc[:6], altered.loc[:6])


def test_temporal_context_resets_each_day():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=4)
    context = build_temporal_context(frame, horizon=3)
    cols = list(temporal_feature_columns(3))
    for day in ("2024-01-02", "2024-01-03"):
        idx = list(frame.index[frame["trading_day"].eq(day)])
        assert context.loc[idx[:2], cols].isna().all().all()
        assert context.loc[idx[2], cols].notna().all()


def test_temporal_context_rejects_non_five_minute_window_even_same_run_id():
    frame = _frame(bars=5)
    frame.loc[2, "market_time_shanghai"] += pd.Timedelta(minutes=5)
    context = build_temporal_context(frame, horizon=3)
    cols = list(temporal_feature_columns(3))
    assert context.loc[2, cols].isna().all()
    assert context.loc[3, cols].isna().all()


def test_v9_promotion_requires_noninferiority_plus_material_gain():
    champion = _champion()
    equal = dict(champion)
    assert not candidate_is_promotable(equal, champion)

    improved = dict(champion)
    improved["min_balanced_accuracy"] += 0.011
    assert candidate_is_promotable(improved, champion)

    improved_but_transition_worse = dict(improved)
    improved_but_transition_worse["min_transition_f1"] -= 0.001
    assert not candidate_is_promotable(improved_but_transition_worse, champion)


def test_v9_selection_keeps_champion_when_no_candidate_passes():
    champion = _champion()
    rows = [
        (TemporalContextCandidate(3, 1.0), dict(champion)),
        (
            TemporalContextCandidate(6, 1.0),
            {
                **champion,
                "min_balanced_accuracy": champion["min_balanced_accuracy"] + 0.02,
                "min_transition_f1": champion["min_transition_f1"] - 0.01,
            },
        ),
    ]
    selected, aggregate, _, _ = select_temporal_candidate(rows, champion)
    assert selected is None
    assert aggregate is None


def test_2025_safety_veto_is_only_for_catastrophic_regression():
    baseline = {
        "000852.SH": {
            "balanced_accuracy_4state": 0.81,
            "macro_f1_4state": 0.80,
            "transition_f1": 0.20,
            "false_transitions_per_day": 1.17,
        },
        "000688.SH": {
            "balanced_accuracy_4state": 0.77,
            "macro_f1_4state": 0.78,
            "transition_f1": 0.19,
            "false_transitions_per_day": 1.05,
        },
    }
    okay = {symbol: dict(metrics) for symbol, metrics in baseline.items()}
    assert not safety_veto_2025(okay, baseline)["veto"]

    bad = {symbol: dict(metrics) for symbol, metrics in baseline.items()}
    bad["000852.SH"]["balanced_accuracy_4state"] -= 0.031
    result = safety_veto_2025(bad, baseline)
    assert result["veto"]
    assert result["failures"]
