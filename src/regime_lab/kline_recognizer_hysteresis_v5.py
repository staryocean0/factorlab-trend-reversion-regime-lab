"""Confidence-aware state persistence for the single K-line recognizer A.

V5 keeps the v4 linear classifier fixed and changes only A's causal state-switch
policy. The frozen v3 independent judge remains an external label/benchmark.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.special import softmax

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_optimization_v4 import (
    CandidateConfig,
    CLASS_NAMES,
    FEATURE_COLUMNS,
    date_mask,
)
from regime_lab.kline_state_recognition import RecognitionConfig, confirmed_states_and_events
from regime_lab.kline_transition_recognition_v2 import classification_for_columns


@dataclass(frozen=True, slots=True)
class HysteresisPolicy:
    switch_margin: float
    min_new_probability: float
    confirmation_bars: int

    def __post_init__(self) -> None:
        if self.switch_margin not in {0.00, 0.05, 0.10, 0.15, 0.20}:
            raise ValueError("switch_margin outside frozen v5 grid")
        if self.min_new_probability not in {0.00, 0.45, 0.55, 0.65}:
            raise ValueError("min_new_probability outside frozen v5 grid")
        if self.confirmation_bars not in {2, 3, 4}:
            raise ValueError("confirmation_bars outside frozen v5 grid")

    def to_dict(self) -> dict[str, object]:
        return {
            "switch_margin": float(self.switch_margin),
            "min_new_probability": float(self.min_new_probability),
            "confirmation_bars": int(self.confirmation_bars),
        }


V4_POLICY = HysteresisPolicy(0.0, 0.0, 3)
V4_LINEAR_CONFIG = CandidateConfig("linear", 3, 1.0)


def frozen_hysteresis_menu() -> tuple[HysteresisPolicy, ...]:
    return tuple(
        HysteresisPolicy(margin, minimum, confirmation)
        for margin in (0.00, 0.05, 0.10, 0.15, 0.20)
        for minimum in (0.00, 0.45, 0.55, 0.65)
        for confirmation in (2, 3, 4)
    )


def _finite_feature_mask(frame: pd.DataFrame) -> pd.Series:
    missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing v5 causal features: {sorted(missing)}")
    values = frame.loc[:, FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    finite = np.isfinite(values.to_numpy(float)).all(axis=1)
    return pd.Series(finite, index=frame.index)


def linear_probabilities(frame: pd.DataFrame, model: Mapping[str, object]) -> pd.DataFrame:
    """Return four-class probabilities from the locked v4 C=1 linear model."""
    if str(model.get("family")) != "linear" or float(model.get("C", math.nan)) != 1.0:
        raise ValueError("v5 requires the locked v4 linear C=1.0 model")
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    weights = np.asarray(model["weights"], dtype=float)
    if weights.shape[0] != len(CLASS_NAMES):
        raise ValueError("unexpected class dimension in v5 linear model")

    out = pd.DataFrame(np.nan, index=frame.index, columns=CLASS_NAMES, dtype=float)
    finite = _finite_feature_mask(frame)
    if finite.any():
        X = frame.loc[finite, FEATURE_COLUMNS].to_numpy(float)
        Z = (X - mean) / scale
        Zb = np.column_stack([np.ones(len(Z)), Z])
        probabilities = softmax(Zb @ weights.T, axis=1)
        out.loc[finite, list(CLASS_NAMES)] = probabilities
    return out


def hysteresis_decode(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
    policy: HysteresisPolicy,
) -> pd.Series:
    """Decode probabilities into one causal state sequence with day-reset memory."""
    if not probabilities.index.equals(frame.index):
        raise ValueError("probability/frame index mismatch")
    if set(CLASS_NAMES) - set(probabilities.columns):
        raise ValueError("missing class probabilities")
    required = {"symbol", "trading_day", "market_time_shanghai", "recognition_eligible"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"hysteresis frame missing columns: {sorted(missing)}")

    decoded = pd.Series("Uncertain", index=frame.index, dtype=object)
    eligible_mask = frame["recognition_eligible"].fillna(False).astype(bool)

    for _, group in frame.loc[eligible_mask].groupby(["symbol", "trading_day"], sort=False):
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
                qualifies = top_probability >= policy.min_new_probability
            elif top_state == current:
                pending = None
                pending_count = 0
                decoded.at[idx] = current
                continue
            else:
                current_probability = float(row[CLASS_NAMES.index(current)])
                qualifies = (
                    top_probability >= policy.min_new_probability
                    and top_probability - current_probability >= policy.switch_margin
                )

            if qualifies:
                if pending == top_state:
                    pending_count += 1
                else:
                    pending = top_state
                    pending_count = 1
                if pending_count >= policy.confirmation_bars:
                    current = top_state
                    pending = None
                    pending_count = 0
            else:
                pending = None
                pending_count = 0

            if current is not None:
                decoded.at[idx] = current

    return decoded


def decoded_events(
    frame: pd.DataFrame,
    decoded: pd.Series,
    *,
    source: str,
) -> pd.DataFrame:
    """Create events from the already-decoded v5 state without a second filter."""
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    eligible["_v5_state"] = decoded.loc[eligible.index].astype(str)
    cfg = replace(RecognitionConfig(), transition_confirm_bars=1)
    _, events = confirmed_states_and_events(
        eligible,
        label_column="_v5_state",
        source=source,
        config=cfg,
    )
    return events


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_policy_period(
    frames: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    model: Mapping[str, object],
    policy: HysteresisPolicy,
    *,
    start: str,
    end: str,
) -> tuple[dict[str, dict[str, object]], dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    results: dict[str, dict[str, object]] = {}
    per_state_tables: dict[str, pd.DataFrame] = {}
    transition_tables: dict[str, pd.DataFrame] = {}

    for symbol in sorted(frames):
        full = frames[symbol]
        part = full.loc[date_mask(full, start, end)].copy()
        probabilities = linear_probabilities(part, model)
        decoded = hysteresis_decode(part, probabilities, policy)
        part["v5_prediction"] = decoded

        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v5_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v5_hysteresis")
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


def aggregate_policy_metrics(
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
    policy: HysteresisPolicy,
    aggregate: Mapping[str, float],
) -> tuple[float, float, float, float, float, float, int]:
    return (
        float(aggregate["min_transition_f1"]),
        -float(aggregate["max_false_transitions_per_day"]),
        float(aggregate["min_balanced_accuracy"]),
        float(aggregate["min_macro_f1"]),
        -float(policy.switch_margin),
        -float(policy.min_new_probability),
        -int(policy.confirmation_bars),
    )


def select_hysteresis_policy(
    rows: list[tuple[HysteresisPolicy, Mapping[str, float]]],
) -> tuple[HysteresisPolicy, Mapping[str, float], bool]:
    eligible = [(policy, aggregate) for policy, aggregate in rows if policy_is_point_eligible(aggregate)]
    if not eligible:
        baseline = next((row for row in rows if row[0] == V4_POLICY), None)
        if baseline is None:
            raise ValueError("v4 baseline policy missing from candidate results")
        return baseline[0], baseline[1], False
    selected = max(eligible, key=lambda item: policy_selection_key(item[0], item[1]))
    return selected[0], selected[1], True


__all__ = [
    "HysteresisPolicy",
    "V4_LINEAR_CONFIG",
    "V4_POLICY",
    "aggregate_policy_metrics",
    "decoded_events",
    "frozen_hysteresis_menu",
    "hysteresis_decode",
    "linear_probabilities",
    "policy_is_point_eligible",
    "policy_selection_key",
    "score_policy_period",
    "select_hysteresis_policy",
]
