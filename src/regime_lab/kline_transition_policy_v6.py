"""Transition policy v6 for the single K-line recognizer A.

This module does not create a new evaluator or model. It only controls when the
existing recognizer is allowed to change its current state.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TransitionPolicy:
    trend_to_range_bars: int = 5
    range_to_trend_bars: int = 3
    enter_shock_bars: int = 1
    exit_shock_bars: int = 5


def classify_transition_type(old: str, new: str) -> str:
    if old == "Shock":
        return "exit_shock"
    if new == "Shock":
        return "enter_shock"
    if old in {"UpTrend", "DownTrend"} and new == "Range":
        return "trend_to_range"
    if old == "Range" and new in {"UpTrend", "DownTrend"}:
        return "range_to_trend"
    return "default"


def transition_requires_confirmation(old: str, new: str, policy: TransitionPolicy | None = None) -> int:
    p = policy or TransitionPolicy()
    kind = classify_transition_type(old, new)
    return {
        "trend_to_range": p.trend_to_range_bars,
        "range_to_trend": p.range_to_trend_bars,
        "enter_shock": p.enter_shock_bars,
        "exit_shock": p.exit_shock_bars,
    }.get(kind, 4)
