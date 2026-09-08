from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES
from regime_lab.kline_transition_policy_v6 import (
    DEFAULT_RULE,
    ENTER_SHOCK_RULES,
    EXIT_SHOCK_RULES,
    RANGE_TO_TREND_RULES,
    TREND_TO_RANGE_RULES,
    TransitionPolicyV6,
    classify_transition_type,
    frozen_transition_policy_menu,
    frozen_v5_baseline,
    select_transition_policy,
    transition_requires_confirmation,
    type_specific_decode,
)


def _frame(days=("2024-01-02",), bars=12):
    rows = []
    for day in days:
        times = pd.date_range(f"{day} 09:30", periods=bars, freq="5min", tz="Asia/Shanghai")
        for ts in times:
            rows.append(
                {
                    "symbol": "000852.SH",
                    "trading_day": day,
                    "market_time_shanghai": ts,
                    "recognition_eligible": True,
                }
            )
    return pd.DataFrame(rows)


def _probs(frame, rows):
    return pd.DataFrame(rows, index=frame.index, columns=CLASS_NAMES, dtype=float)


def _all_fast_policy():
    return TransitionPolicyV6(
        candidate_id="test_fast",
        trend_to_range=TREND_TO_RANGE_RULES[0],
        range_to_trend=RANGE_TO_TREND_RULES[0],
        enter_shock=ENTER_SHOCK_RULES[0],
        exit_shock=EXIT_SHOCK_RULES[0],
    )


def test_transition_types_are_explicit():
    assert classify_transition_type("UpTrend", "Range") == "trend_to_range"
    assert classify_transition_type("Range", "UpTrend") == "range_to_trend"
    assert classify_transition_type("Range", "Shock") == "enter_shock"
    assert classify_transition_type("Shock", "Range") == "exit_shock"
    assert classify_transition_type("UpTrend", "DownTrend") == "default"


def test_frozen_menu_is_exactly_16_typed_plus_v5_baseline():
    menu = frozen_transition_policy_menu()
    assert len(menu) == 17
    assert len({p.candidate_id for p in menu}) == 17
    typed = [p for p in menu if not p.universal_baseline]
    baseline = [p for p in menu if p.universal_baseline]
    assert len(typed) == 16
    assert len(baseline) == 1
    assert baseline[0] == frozen_v5_baseline()


def test_shock_entry_is_faster_than_release_and_trend_exit():
    policy = _all_fast_policy()
    assert transition_requires_confirmation("Range", "Shock", policy) == 1
    assert transition_requires_confirmation("Shock", "Range", policy) == 4
    assert transition_requires_confirmation("UpTrend", "Range", policy) == 4
    assert transition_requires_confirmation("Range", "UpTrend", policy) == 3


def test_default_transition_uses_v5_rule():
    policy = _all_fast_policy()
    assert policy.rule_for("UpTrend", "DownTrend") == DEFAULT_RULE
    assert transition_requires_confirmation("UpTrend", "DownTrend", policy) == 4


def test_decoder_enters_shock_immediately_after_initial_state_is_established():
    frame = _frame(bars=6)
    probabilities = _probs(
        frame,
        [
            [0.75, 0.10, 0.10, 0.05],
            [0.76, 0.09, 0.10, 0.05],
            [0.77, 0.08, 0.10, 0.05],
            [0.78, 0.07, 0.10, 0.05],  # initial UpTrend confirms here (default 4)
            [0.10, 0.05, 0.10, 0.75],  # Shock fast rule: 1 bar
            [0.10, 0.05, 0.10, 0.75],
        ],
    )
    decoded = type_specific_decode(frame, probabilities, _all_fast_policy())
    assert decoded.iloc[2] == "Uncertain"
    assert decoded.iloc[3] == "UpTrend"
    assert decoded.iloc[4] == "Shock"


def test_decoder_requires_four_bars_to_exit_shock_under_fast_release_rule():
    frame = _frame(bars=9)
    probabilities = _probs(
        frame,
        [
            [0.10, 0.05, 0.10, 0.75],
            [0.10, 0.05, 0.10, 0.75],
            [0.10, 0.05, 0.10, 0.75],
            [0.10, 0.05, 0.10, 0.75],  # initial Shock after 4 default bars
            [0.10, 0.05, 0.75, 0.10],
            [0.10, 0.05, 0.75, 0.10],
            [0.10, 0.05, 0.75, 0.10],
            [0.10, 0.05, 0.75, 0.10],  # Range confirms after 4 exit bars
            [0.10, 0.05, 0.75, 0.10],
        ],
    )
    decoded = type_specific_decode(frame, probabilities, _all_fast_policy())
    assert decoded.iloc[3] == "Shock"
    assert decoded.iloc[6] == "Shock"
    assert decoded.iloc[7] == "Range"


def test_decoder_resets_memory_each_trading_day():
    frame = _frame(days=("2024-01-02", "2024-01-03"), bars=4)
    probabilities = _probs(
        frame,
        [[0.8, 0.05, 0.10, 0.05]] * 4 + [[0.05, 0.8, 0.10, 0.05]] * 4,
    )
    decoded = type_specific_decode(frame, probabilities, _all_fast_policy())
    assert decoded.iloc[3] == "UpTrend"
    assert decoded.iloc[4] == "Uncertain"
    assert decoded.iloc[7] == "DownTrend"


def test_decoder_requires_probability_margin_for_strict_trend_to_range():
    strict = TransitionPolicyV6(
        candidate_id="strict",
        trend_to_range=TREND_TO_RANGE_RULES[1],
        range_to_trend=RANGE_TO_TREND_RULES[0],
        enter_shock=ENTER_SHOCK_RULES[0],
        exit_shock=EXIT_SHOCK_RULES[0],
    )
    frame = _frame(bars=10)
    rows = [[0.75, 0.05, 0.15, 0.05]] * 4
    # Range leads UpTrend by only 0.06 (< strict 0.10), so no switch despite 5 bars.
    rows += [[0.42, 0.03, 0.48, 0.07]] * 6
    decoded = type_specific_decode(frame, _probs(frame, rows), strict)
    assert decoded.iloc[3] == "UpTrend"
    assert decoded.iloc[-1] == "UpTrend"


def test_selector_uses_point_floors_and_prefers_transition_f1():
    menu = frozen_transition_policy_menu()
    a, b = menu[0], menu[1]
    baseline = frozen_v5_baseline()
    common = {"min_balanced_accuracy": 0.80, "min_macro_f1": 0.78}
    rows = [
        (a, {**common, "min_transition_f1": 0.25, "max_false_transitions_per_day": 0.8}),
        (b, {**common, "min_transition_f1": 0.30, "max_false_transitions_per_day": 0.9}),
        (baseline, {**common, "min_transition_f1": 0.40, "max_false_transitions_per_day": 0.5}),
    ]
    selected, _, typed_available = select_transition_policy(rows)
    assert typed_available
    assert selected == b


def test_selector_falls_back_to_baseline_if_no_typed_candidate_passes_point_floors():
    typed = frozen_transition_policy_menu()[0]
    baseline = frozen_v5_baseline()
    rows = [
        (
            typed,
            {
                "min_balanced_accuracy": 0.74,
                "min_macro_f1": 0.80,
                "min_transition_f1": 0.40,
                "max_false_transitions_per_day": 0.4,
            },
        ),
        (
            baseline,
            {
                "min_balanced_accuracy": 0.75,
                "min_macro_f1": 0.73,
                "min_transition_f1": 0.20,
                "max_false_transitions_per_day": 1.0,
            },
        ),
    ]
    selected, _, typed_available = select_transition_policy(rows)
    assert not typed_available
    assert selected.universal_baseline


def test_probability_rows_can_be_regular_float_arrays():
    frame = _frame(bars=4)
    probs = np.array([[0.8, 0.05, 0.10, 0.05]] * 4)
    decoded = type_specific_decode(frame, pd.DataFrame(probs, columns=CLASS_NAMES), _all_fast_policy())
    assert decoded.iloc[-1] == "UpTrend"
