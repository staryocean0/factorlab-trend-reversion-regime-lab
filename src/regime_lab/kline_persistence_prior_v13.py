"""V13: one-step low-weight persistence prior integrated into champion v10.

The historical v7 transition matrix contributes only a weak predictive prior.
There is no recursive Markov posterior and no Markov argmax decoder.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.special import logsumexp

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_markov_filter_v7 import sharpen_transition_matrix
from regime_lab.kline_recognizer_hysteresis_v5 import decoded_events, hysteresis_decode, linear_probabilities
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
TRANSITION_ETA = 2.0


@dataclass(frozen=True, slots=True)
class PersistencePriorCandidate:
    rho: float

    def __post_init__(self) -> None:
        if self.rho not in {0.05, 0.10, 0.15}:
            raise ValueError("v13 rho outside frozen grid")

    @property
    def candidate_id(self) -> str:
        return f"persistence_rho{self.rho:.2f}"

    def to_dict(self) -> dict[str, object]:
        return {"rho": float(self.rho), "transition_eta": TRANSITION_ETA}


def frozen_persistence_menu() -> tuple[PersistencePriorCandidate, ...]:
    return tuple(PersistencePriorCandidate(rho) for rho in (0.05, 0.10, 0.15))


def one_step_persistence_probabilities(
    frame: pd.DataFrame,
    base_probabilities: pd.DataFrame,
    markov_model: Mapping[str, object],
    candidate: PersistencePriorCandidate,
) -> pd.DataFrame:
    """Blend only the immediately previous base-v10 probability into current evidence.

    This function is deliberately non-recursive: the previous *output* from this
    function is never used to form the next prior.
    """
    if not base_probabilities.index.equals(frame.index):
        raise ValueError("v13 probability/frame index mismatch")
    if set(CLASS_NAMES) - set(base_probabilities.columns):
        raise ValueError("v13 missing class probabilities")
    required = {"symbol", "trading_day", "market_time_shanghai"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v13 frame missing columns: {sorted(missing)}")

    transition = sharpen_transition_matrix(
        np.asarray(markov_model["transition_matrix"], dtype=float), TRANSITION_ETA
    )
    out = pd.DataFrame(np.nan, index=frame.index, columns=CLASS_NAMES, dtype=float)
    eps = 1e-15

    for _, day in frame.groupby(["symbol", "trading_day"], sort=False):
        ordered = day.sort_values("market_time_shanghai", kind="stable")
        previous_base: np.ndarray | None = None
        for idx in ordered.index:
            current = base_probabilities.loc[idx, list(CLASS_NAMES)].to_numpy(float)
            current_ok = np.isfinite(current).all() and (current >= 0).all() and float(current.sum()) > 0.0
            if not current_ok:
                previous_base = None
                continue
            current = current / current.sum()

            if previous_base is None:
                final = current
            else:
                predictive = previous_base @ transition
                predictive = predictive / predictive.sum()
                logp = np.log(np.clip(current, eps, 1.0))
                logp += float(candidate.rho) * np.log(np.clip(predictive, eps, 1.0))
                logp -= logsumexp(logp)
                final = np.exp(logp)

            out.loc[idx, list(CLASS_NAMES)] = final
            # Critical: retain the base-v10 current row, not v13 final posterior.
            previous_base = current

    return out


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_persistence_period(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    primary_model: Mapping[str, object],
    temporal_model: Mapping[str, object],
    markov_model: Mapping[str, object],
    candidate: PersistencePriorCandidate,
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
        base = blend_probabilities(primary, temporal, alpha=V10_BLEND.alpha)
        adjusted = one_step_persistence_probabilities(part, base, markov_model, candidate)
        decoded = hysteresis_decode(part, adjusted, V5_POLICY)
        part["v13_prediction"] = decoded

        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v13_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v13_persistence_prior")
        judge = _filter_events(judge_events[symbol], start=start, end=end)
        transition_table, transition_summary, _ = compare_independent_transitions(
            part, events, judge, config=RecognitionConfig()
        )
        results[symbol] = {**point, **transition_summary}
        per_state_tables[symbol] = per_state
        transition_tables[symbol] = transition_table

    return results, per_state_tables, transition_tables


def candidate_is_promotable(
    aggregate: Mapping[str, float], champion: Mapping[str, float]
) -> bool:
    noninferior = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"])
        and float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"])
        and float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"])
        and float(aggregate["max_false_transitions_per_day"]) <= float(champion["max_false_transitions_per_day"])
    )
    material = (
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"]) + 0.01
        or float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"]) + 0.01
        or float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"]) + 0.01
        or float(aggregate["max_false_transitions_per_day"]) <= float(champion["max_false_transitions_per_day"]) - 0.05
    )
    return bool(noninferior and material)


def select_persistence_candidate(
    rows: list[tuple[PersistencePriorCandidate, Mapping[str, float]]],
    champion: Mapping[str, float],
) -> tuple[PersistencePriorCandidate | None, Mapping[str, float] | None, PersistencePriorCandidate, Mapping[str, float]]:
    if not rows:
        raise ValueError("v13 candidate rows empty")
    key = lambda item: (
        float(item[1]["min_transition_f1"]),
        -float(item[1]["max_false_transitions_per_day"]),
        float(item[1]["min_balanced_accuracy"]),
        float(item[1]["min_macro_f1"]),
        -float(item[0].rho),
    )
    best, best_aggregate = max(rows, key=key)
    eligible = [(c, a) for c, a in rows if candidate_is_promotable(a, champion)]
    if not eligible:
        return None, None, best, best_aggregate
    selected, aggregate = max(eligible, key=key)
    return selected, aggregate, best, best_aggregate


__all__ = [
    "PersistencePriorCandidate",
    "TRANSITION_ETA",
    "V10_BLEND",
    "aggregate_fold_metrics",
    "candidate_is_promotable",
    "frozen_persistence_menu",
    "one_step_persistence_probabilities",
    "safety_veto_2025",
    "score_persistence_period",
    "select_persistence_candidate",
]
