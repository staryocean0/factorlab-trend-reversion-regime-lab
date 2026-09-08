"""Type-specific causal transition policy for the single K-line recognizer A.

V6 keeps the v4-selected linear classifier, causal feature surface and frozen v3
benchmark unchanged. Only A's state-switch decision rule changes.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Mapping

import numpy as np
import pandas as pd

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_hysteresis_v5 import linear_probabilities
from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES, date_mask
from regime_lab.kline_state_recognition import RecognitionConfig, confirmed_states_and_events
from regime_lab.kline_transition_recognition_v2 import classification_for_columns


@dataclass(frozen=True, slots=True)
class SwitchRule:
    margin: float
    min_probability: float
    confirmation_bars: int

    def to_dict(self) -> dict[str, object]:
        return {
            "margin": float(self.margin),
            "min_probability": float(self.min_probability),
            "confirmation_bars": int(self.confirmation_bars),
        }


TREND_TO_RANGE_RULES = (
    SwitchRule(0.05, 0.45, 4),
    SwitchRule(0.10, 0.55, 5),
)
RANGE_TO_TREND_RULES = (
    SwitchRule(0.05, 0.45, 3),
    SwitchRule(0.10, 0.55, 4),
)
ENTER_SHOCK_RULES = (
    SwitchRule(0.00, 0.45, 1),
    SwitchRule(0.05, 0.55, 2),
)
EXIT_SHOCK_RULES = (
    SwitchRule(0.05, 0.45, 4),
    SwitchRule(0.10, 0.55, 5),
)
DEFAULT_RULE = SwitchRule(0.05, 0.45, 4)


@dataclass(frozen=True, slots=True)
class TransitionPolicyV6:
    candidate_id: str
    trend_to_range: SwitchRule
    range_to_trend: SwitchRule
    enter_shock: SwitchRule
    exit_shock: SwitchRule
    universal_baseline: bool = False

    def rule_for(self, old: str, new: str) -> SwitchRule:
        if self.universal_baseline:
            return DEFAULT_RULE
        kind = classify_transition_type(old, new)
        return {
            "trend_to_range": self.trend_to_range,
            "range_to_trend": self.range_to_trend,
            "enter_shock": self.enter_shock,
            "exit_shock": self.exit_shock,
        }.get(kind, DEFAULT_RULE)

    def to_dict(self) -> dict[str, object]:
        return {
            "candidate_id": self.candidate_id,
            "universal_baseline": bool(self.universal_baseline),
            "trend_to_range": self.trend_to_range.to_dict(),
            "range_to_trend": self.range_to_trend.to_dict(),
            "enter_shock": self.enter_shock.to_dict(),
            "exit_shock": self.exit_shock.to_dict(),
            "default": DEFAULT_RULE.to_dict(),
        }

    def complexity_tuple(self) -> tuple[int, float, float]:
        rules = (self.trend_to_range, self.range_to_trend, self.enter_shock, self.exit_shock)
        return (
            sum(rule.confirmation_bars for rule in rules),
            float(sum(rule.margin for rule in rules)),
            float(sum(rule.min_probability for rule in rules)),
        )


def classify_transition_type(old: str, new: str) -> str:
    if old == "Shock" and new != "Shock":
        return "exit_shock"
    if old != "Shock" and new == "Shock":
        return "enter_shock"
    if old in {"UpTrend", "DownTrend"} and new == "Range":
        return "trend_to_range"
    if old == "Range" and new in {"UpTrend", "DownTrend"}:
        return "range_to_trend"
    return "default"


def transition_requires_confirmation(
    old: str,
    new: str,
    policy: TransitionPolicyV6 | None = None,
) -> int:
    p = policy or frozen_v5_baseline()
    return int(p.rule_for(old, new).confirmation_bars)


def frozen_v5_baseline() -> TransitionPolicyV6:
    return TransitionPolicyV6(
        candidate_id="v5_universal",
        trend_to_range=DEFAULT_RULE,
        range_to_trend=DEFAULT_RULE,
        enter_shock=DEFAULT_RULE,
        exit_shock=DEFAULT_RULE,
        universal_baseline=True,
    )


def frozen_transition_policy_menu() -> tuple[TransitionPolicyV6, ...]:
    rows: list[TransitionPolicyV6] = []
    for t_idx, t_rule in enumerate(TREND_TO_RANGE_RULES):
        for r_idx, r_rule in enumerate(RANGE_TO_TREND_RULES):
            for e_idx, e_rule in enumerate(ENTER_SHOCK_RULES):
                for x_idx, x_rule in enumerate(EXIT_SHOCK_RULES):
                    rows.append(
                        TransitionPolicyV6(
                            candidate_id=f"v6_t{t_idx}r{r_idx}e{e_idx}x{x_idx}",
                            trend_to_range=t_rule,
                            range_to_trend=r_rule,
                            enter_shock=e_rule,
                            exit_shock=x_rule,
                        )
                    )
    rows.append(frozen_v5_baseline())
    return tuple(rows)


def type_specific_decode(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
    policy: TransitionPolicyV6,
) -> pd.Series:
    """Decode four-class probabilities with transition-type-specific hysteresis."""
    if not probabilities.index.equals(frame.index):
        raise ValueError("probability/frame index mismatch")
    if set(CLASS_NAMES) - set(probabilities.columns):
        raise ValueError("missing class probabilities")
    required = {"symbol", "trading_day", "market_time_shanghai", "recognition_eligible"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v6 decoder frame missing columns: {sorted(missing)}")

    decoded = pd.Series("Uncertain", index=frame.index, dtype=object)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)

    for _, group in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        current: str | None = None
        pending: str | None = None
        pending_count = 0

        for idx in ordered.index:
            row = probabilities.loc[idx, list(CLASS_NAMES)].to_numpy(float)
            if not np.isfinite(row).all():
                if current is not None:
                    decoded.at[idx] = current
                continue

            top_id = int(np.argmax(row))
            top_state = str(CLASS_NAMES[top_id])
            top_probability = float(row[top_id])

            if current is None:
                rule = DEFAULT_RULE
                qualifies = top_probability >= rule.min_probability
            elif top_state == current:
                pending = None
                pending_count = 0
                decoded.at[idx] = current
                continue
            else:
                rule = policy.rule_for(current, top_state)
                current_probability = float(row[CLASS_NAMES.index(current)])
                qualifies = (
                    top_probability >= rule.min_probability
                    and top_probability - current_probability >= rule.margin
                )

            if qualifies:
                if pending == top_state:
                    pending_count += 1
                else:
                    pending = top_state
                    pending_count = 1
                if pending_count >= rule.confirmation_bars:
                    current = top_state
                    pending = None
                    pending_count = 0
            else:
                pending = None
                pending_count = 0

            if current is not None:
                decoded.at[idx] = current

    return decoded


def decoded_events(frame: pd.DataFrame, decoded: pd.Series, *, source: str) -> pd.DataFrame:
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    eligible["_v6_state"] = decoded.loc[eligible.index].astype(str)
    cfg = replace(RecognitionConfig(), transition_confirm_bars=1)
    _, events = confirmed_states_and_events(
        eligible,
        label_column="_v6_state",
        source=source,
        config=cfg,
    )
    return events


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_policy_period_from_probabilities(
    frames: Mapping[str, pd.DataFrame],
    probabilities: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    policy: TransitionPolicyV6,
    *,
    start: str,
    end: str,
) -> tuple[dict[str, dict[str, object]], dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    results: dict[str, dict[str, object]] = {}
    per_state_tables: dict[str, pd.DataFrame] = {}
    transition_tables: dict[str, pd.DataFrame] = {}

    for symbol in sorted(frames):
        full = frames[symbol]
        mask = date_mask(full, start, end)
        part = full.loc[mask].copy()
        probs = probabilities[symbol].loc[part.index]
        decoded = type_specific_decode(part, probs, policy)
        part["v6_prediction"] = decoded
        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v6_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source=f"v6_{policy.candidate_id}")
        judge = _filter_events(judge_events[symbol], start=start, end=end)
        transition_table, transition_summary, _ = compare_independent_transitions(
            part,
            events,
            judge,
            config=RecognitionConfig(),
        )
        results[symbol] = {**point, **transition_summary}
        per_state_tables[symbol] = per_state
        transition_tables[symbol] = transition_table
    return results, per_state_tables, transition_tables


def score_policy_period(
    frames: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    model: Mapping[str, object],
    policy: TransitionPolicyV6,
    *,
    start: str,
    end: str,
) -> tuple[dict[str, dict[str, object]], dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    probabilities = {symbol: linear_probabilities(frame, model) for symbol, frame in frames.items()}
    return score_policy_period_from_probabilities(
        frames,
        probabilities,
        judge_events,
        policy,
        start=start,
        end=end,
    )


def aggregate_fold_metrics(
    fold_results: Mapping[str, Mapping[str, Mapping[str, object]]]
) -> dict[str, float]:
    cells = [metrics for fold in fold_results.values() for metrics in fold.values()]
    return {
        "min_balanced_accuracy": min(float(cell["balanced_accuracy_4state"]) for cell in cells),
        "min_macro_f1": min(float(cell["macro_f1_4state"]) for cell in cells),
        "min_transition_f1": min(float(cell["transition_f1"]) for cell in cells),
        "max_false_transitions_per_day": max(float(cell["false_transitions_per_day"]) for cell in cells),
        "mean_false_transitions_per_day": float(
            np.mean([float(cell["false_transitions_per_day"]) for cell in cells])
        ),
    }


def policy_is_point_eligible(aggregate: Mapping[str, float]) -> bool:
    return (
        float(aggregate["min_balanced_accuracy"]) >= 0.75
        and float(aggregate["min_macro_f1"]) >= 0.72
    )


def policy_selection_key(
    policy: TransitionPolicyV6,
    aggregate: Mapping[str, float],
) -> tuple[float, float, float, float, int, float, float, str]:
    confirmations, margins, minima = policy.complexity_tuple()
    return (
        float(aggregate["min_transition_f1"]),
        -float(aggregate["max_false_transitions_per_day"]),
        float(aggregate["min_balanced_accuracy"]),
        float(aggregate["min_macro_f1"]),
        -int(confirmations),
        -float(margins),
        -float(minima),
        policy.candidate_id,
    )


def select_transition_policy(
    rows: list[tuple[TransitionPolicyV6, Mapping[str, float]]],
) -> tuple[TransitionPolicyV6, Mapping[str, float], bool]:
    if not rows:
        raise ValueError("v6 candidate rows are empty")
    eligible = [(policy, aggregate) for policy, aggregate in rows if policy_is_point_eligible(aggregate)]
    typed = [(policy, aggregate) for policy, aggregate in eligible if not policy.universal_baseline]
    if not typed:
        baseline = next((row for row in rows if row[0].universal_baseline), None)
        if baseline is None:
            raise ValueError("v5 universal baseline missing from v6 menu")
        return baseline[0], baseline[1], False
    selected = max(typed, key=lambda item: policy_selection_key(item[0], item[1]))
    return selected[0], selected[1], True


def diagnostic_success(
    selected: Mapping[str, Mapping[str, object]],
    baseline: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    stronger_failures: list[str] = []
    for symbol in ("000852.SH", "000688.SH"):
        s = selected[symbol]
        b = baseline[symbol]
        if float(s["transition_f1"]) < float(b["transition_f1"]):
            failures.append(f"{symbol}: transition_f1 below v5")
        if float(s["false_transitions_per_day"]) >= float(b["false_transitions_per_day"]):
            failures.append(f"{symbol}: false_transitions_per_day not reduced")
        if float(s["balanced_accuracy_4state"]) < 0.75:
            failures.append(f"{symbol}: balanced_accuracy < 0.75")
        if float(s["macro_f1_4state"]) < 0.72:
            failures.append(f"{symbol}: macro_f1 < 0.72")
        if float(s["transition_f1"]) < 0.30:
            stronger_failures.append(f"{symbol}: transition_f1 < 0.30")
        if float(s["false_transitions_per_day"]) > 0.80:
            stronger_failures.append(f"{symbol}: false_transitions_per_day > 0.80")
    return {
        "status": "useful_v6_improvement" if not failures else "v6_not_yet_useful",
        "failures": failures,
        "strong_target_passed": not stronger_failures,
        "strong_target_failures": stronger_failures,
    }


__all__ = [
    "DEFAULT_RULE",
    "ENTER_SHOCK_RULES",
    "EXIT_SHOCK_RULES",
    "RANGE_TO_TREND_RULES",
    "SwitchRule",
    "TREND_TO_RANGE_RULES",
    "TransitionPolicyV6",
    "aggregate_fold_metrics",
    "classify_transition_type",
    "decoded_events",
    "diagnostic_success",
    "frozen_transition_policy_menu",
    "frozen_v5_baseline",
    "policy_is_point_eligible",
    "policy_selection_key",
    "score_policy_period",
    "score_policy_period_from_probabilities",
    "select_transition_policy",
    "transition_requires_confirmation",
    "type_specific_decode",
]
