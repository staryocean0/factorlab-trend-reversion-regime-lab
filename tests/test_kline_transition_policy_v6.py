from __future__ import annotations

import pandas as pd

from regime_lab.kline_transition_policy_v6 import (
    TransitionPolicy,
    classify_transition_type,
    transition_requires_confirmation,
)


def test_transition_types_are_explicit():
    assert classify_transition_type("UpTrend", "Range") == "trend_to_range"
    assert classify_transition_type("Range", "UpTrend") == "range_to_trend"
    assert classify_transition_type("Range", "Shock") == "enter_shock"
    assert classify_transition_type("Shock", "Range") == "exit_shock"


def test_shock_entry_is_fast_and_trend_break_is_slow():
    assert transition_requires_confirmation("Range", "Shock") < transition_requires_confirmation("UpTrend", "Range")
    assert transition_requires_confirmation("Shock", "Range") > transition_requires_confirmation("Range", "Shock")


def test_unknown_transition_uses_safe_default():
    assert transition_requires_confirmation("A", "B") == 4
