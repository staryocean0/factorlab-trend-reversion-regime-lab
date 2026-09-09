"""V12: integrate the audited v6 Shock-exit asymmetry into champion v10.

Only a soft log-odds bonus for staying in Shock is added while the current
causal decoded state is Shock. The v10 primary/temporal heads, alpha=0.30 blend,
and ordinary v5 hysteresis behavior are otherwise unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_hysteresis_v5 import decoded_events, linear_probabilities
from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES, date_mask
from regime_lab.kline_state_recognition import RecognitionConfig
from regime_lab.kline_temporal_blend_v10 import (
    TemporalBlendCandidate,
    V5_POLICY,
    aggregate_fold_metrics,
    blend_probabilities,
    safety_veto_2025,
)
from regime_lab.kline_temporal_context_v9 import temporal_probabilities
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

V10_BLEND = TemporalBlendCandidate(6, 0.30)
SHOCK = "Shock"


@dataclass(frozen=True, slots=True)
class ShockExitInertiaCandidate:
    gamma: float

    def __post_init__(self) -> None:
        if self.gamma not in {0.10, 0.20, 0.30}:
            raise ValueError("v12 gamma outside frozen grid")

    @property
    def candidate_id(self) -> str:
        return f"shock_exit_gamma{self.gamma:.2f}"

    def to_dict(self) -> dict[str, object]:
        return {"gamma": float(self.gamma)}


def frozen_shock_exit_menu() -> tuple[ShockExitInertiaCandidate, ...]:
    return tuple(ShockExitInertiaCandidate(g) for g in (0.10, 0.20, 0.30))


def _shock_bonus(row: np.ndarray, gamma: float) -> np.ndarray:
    out = np.asarray(row, dtype=float).copy()
    if not np.isfinite(out).all():
        return out
    shock_i = CLASS_NAMES.index(SHOCK)
    out[shock_i] *= float(np.exp(gamma))
    total = float(out.sum())
    if not np.isfinite(total) or total <= 0.0:
        return np.full_like(out, np.nan)
    return out / total


def shock_exit_inertia_decode(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
    candidate: ShockExitInertiaCandidate,
) -> pd.Series:
    """Causal day-reset v5 decoder with a soft bonus only while leaving Shock."""
    if not probabilities.index.equals(frame.index):
        raise ValueError("probability/frame index mismatch")
    if set(CLASS_NAMES) - set(probabilities.columns):
        raise ValueError("missing class probabilities")
    required = {"symbol", "trading_day", "market_time_shanghai", "recognition_eligible"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v12 frame missing columns: {sorted(missing)}")

    decoded = pd.Series("Uncertain", index=frame.index, dtype=object)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)

    for _, group in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        current: str | None = None
        pending: str | None = None
        pending_count = 0

        for idx in ordered.index:
            row = probabilities.loc[idx, list(CLASS_NAMES)].to_numpy(float)
            if current == SHOCK:
                row = _shock_bonus(row, candidate.gamma)

            if not np.isfinite(row).all():
                if current is not None:
                    decoded.at[idx] = current
                continue

            top_id = int(np.argmax(row))
            top_state = str(CLASS_NAMES[top_id])
            top_probability = float(row[top_id])

            if current is None:
                qualifies = top_probability >= V5_POLICY.min_new_probability
            elif top_state == current:
                pending = None
                pending_count = 0
                decoded.at[idx] = current
                continue
            else:
                current_probability = float(row[CLASS_NAMES.index(current)])
                qualifies = (
                    top_probability >= V5_POLICY.min_new_probability
                    and top_probability - current_probability >= V5_POLICY.switch_margin
                )

            if qualifies:
                if pending == top_state:
                    pending_count += 1
                else:
                    pending = top_state
                    pending_count = 1
                if pending_count >= V5_POLICY.confirmation_bars:
                    current = top_state
                    pending = None
                    pending_count = 0
            else:
                pending = None
                pending_count = 0

            if current is not None:
                decoded.at[idx] = current

    return decoded


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_shock_exit_period(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    primary_model: Mapping[str, object],
    temporal_model: Mapping[str, object],
    candidate: ShockExitInertiaCandidate,
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
        context = contexts[symbol].loc[part.index]

        primary = linear_probabilities(part, primary_model)
        temporal = temporal_probabilities(context, temporal_model)
        blended = blend_probabilities(primary, temporal, alpha=V10_BLEND.alpha)
        decoded = shock_exit_inertia_decode(part, blended, candidate)
        part["v12_prediction"] = decoded

        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v12_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v12_shock_exit_inertia")
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


def candidate_is_promotable(
    aggregate: Mapping[str, float],
    champion: Mapping[str, float],
) -> bool:
    noninferior = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"])
        and float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"])
        and float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"])
        and float(aggregate["max_false_transitions_per_day"])
        <= float(champion["max_false_transitions_per_day"])
    )
    material = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"]) + 0.01
        or float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"]) + 0.01
        or float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"]) + 0.01
        or float(aggregate["max_false_transitions_per_day"])
        <= float(champion["max_false_transitions_per_day"]) - 0.05
    )
    return bool(noninferior and material)


def select_shock_exit_candidate(
    rows: list[tuple[ShockExitInertiaCandidate, Mapping[str, float]]],
    champion: Mapping[str, float],
) -> tuple[ShockExitInertiaCandidate | None, Mapping[str, float] | None, ShockExitInertiaCandidate, Mapping[str, float]]:
    best, best_agg = max(
        rows,
        key=lambda item: (
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            -float(item[0].gamma),
        ),
    )
    eligible = [(c, a) for c, a in rows if candidate_is_promotable(a, champion)]
    if not eligible:
        return None, None, best, best_agg
    selected, aggregate = max(
        eligible,
        key=lambda item: (
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            -float(item[0].gamma),
        ),
    )
    return selected, aggregate, best, best_agg


__all__ = [
    "ShockExitInertiaCandidate",
    "V10_BLEND",
    "aggregate_fold_metrics",
    "candidate_is_promotable",
    "frozen_shock_exit_menu",
    "safety_veto_2025",
    "score_shock_exit_period",
    "select_shock_exit_candidate",
    "shock_exit_inertia_decode",
]
