"""V10: integrate retained temporal-context contribution into the v5 champion.

The v5 current-state classifier stays primary and the v5 hysteresis decoder stays
unchanged. A v9 temporal model contributes only a small log-probability blend.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.special import logsumexp

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_hysteresis_v5 import (
    HysteresisPolicy,
    decoded_events,
    hysteresis_decode,
    linear_probabilities,
)
from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES, date_mask
from regime_lab.kline_state_recognition import RecognitionConfig
from regime_lab.kline_temporal_context_v9 import temporal_probabilities
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

V5_POLICY = HysteresisPolicy(0.05, 0.45, 4)
AUXILIARY_C = 0.1


@dataclass(frozen=True, slots=True)
class TemporalBlendCandidate:
    horizon: int
    alpha: float

    def __post_init__(self) -> None:
        if self.horizon not in {3, 6}:
            raise ValueError("v10 horizon outside frozen grid")
        if self.alpha not in {0.10, 0.20, 0.30}:
            raise ValueError("v10 alpha outside frozen grid")

    @property
    def candidate_id(self) -> str:
        return f"blend_h{self.horizon}_a{self.alpha:.2f}"

    def to_dict(self) -> dict[str, object]:
        return {
            "horizon": int(self.horizon),
            "alpha": float(self.alpha),
            "auxiliary_C": AUXILIARY_C,
        }


def frozen_blend_menu() -> tuple[TemporalBlendCandidate, ...]:
    return tuple(
        TemporalBlendCandidate(horizon, alpha)
        for horizon in (3, 6)
        for alpha in (0.10, 0.20, 0.30)
    )


def blend_probabilities(
    primary: pd.DataFrame,
    temporal: pd.DataFrame,
    *,
    alpha: float,
) -> pd.DataFrame:
    """Blend temporal evidence into primary probabilities without reducing coverage.

    If temporal context is unavailable, return the primary probability row exactly.
    If primary is unavailable, the auxiliary head is forbidden from creating output.
    """
    if alpha < 0.0 or alpha >= 0.5:
        raise ValueError("v10 blend requires 0 <= alpha < 0.5")
    if not primary.index.equals(temporal.index):
        raise ValueError("primary/temporal index mismatch")
    if set(CLASS_NAMES) - set(primary.columns) or set(CLASS_NAMES) - set(temporal.columns):
        raise ValueError("missing class probabilities")

    p = primary.loc[:, list(CLASS_NAMES)].to_numpy(float)
    t = temporal.loc[:, list(CLASS_NAMES)].to_numpy(float)
    out = np.full_like(p, np.nan, dtype=float)

    p_ok = np.isfinite(p).all(axis=1)
    t_ok = np.isfinite(t).all(axis=1)

    # Champion fallback: temporal absence must not remove a valid primary prediction.
    out[p_ok] = p[p_ok]

    both = p_ok & t_ok
    if both.any():
        eps = 1e-15
        logp = (1.0 - alpha) * np.log(np.clip(p[both], eps, 1.0))
        logp += alpha * np.log(np.clip(t[both], eps, 1.0))
        logp -= logsumexp(logp, axis=1)[:, None]
        out[both] = np.exp(logp)

    return pd.DataFrame(out, index=primary.index, columns=CLASS_NAMES, dtype=float)


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_blend_period(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    primary_model: Mapping[str, object],
    temporal_model: Mapping[str, object],
    candidate: TemporalBlendCandidate,
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
        context = contexts[symbol].loc[part.index]

        primary = linear_probabilities(part, primary_model)
        temporal = temporal_probabilities(context, temporal_model)
        blended = blend_probabilities(primary, temporal, alpha=candidate.alpha)
        decoded = hysteresis_decode(part, blended, V5_POLICY)
        part["v10_prediction"] = decoded

        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v10_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v10_temporal_blend")
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


def aggregate_fold_metrics(
    fold_results: Mapping[str, Mapping[str, Mapping[str, object]]]
) -> dict[str, float]:
    cells = [metrics for fold in fold_results.values() for metrics in fold.values()]
    return {
        "min_balanced_accuracy": min(float(x["balanced_accuracy_4state"]) for x in cells),
        "min_macro_f1": min(float(x["macro_f1_4state"]) for x in cells),
        "min_transition_f1": min(float(x["transition_f1"]) for x in cells),
        "max_false_transitions_per_day": max(float(x["false_transitions_per_day"]) for x in cells),
        "mean_false_transitions_per_day": float(
            np.mean([float(x["false_transitions_per_day"]) for x in cells])
        ),
    }


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


def select_blend_candidate(
    rows: list[tuple[TemporalBlendCandidate, Mapping[str, float]]],
    champion: Mapping[str, float],
) -> tuple[TemporalBlendCandidate | None, Mapping[str, float] | None]:
    eligible = [(c, a) for c, a in rows if candidate_is_promotable(a, champion)]
    if not eligible:
        return None, None
    return max(
        eligible,
        key=lambda item: (
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            -float(item[0].alpha),
            -int(item[0].horizon),
        ),
    )


def safety_veto_2025(
    challenger: Mapping[str, Mapping[str, object]],
    champion: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    for symbol in sorted(challenger):
        c = challenger[symbol]
        b = champion[symbol]
        checks = (
            ("balanced_accuracy_4state", float(c["balanced_accuracy_4state"]), float(b["balanced_accuracy_4state"]), 0.01, "lower"),
            ("macro_f1_4state", float(c["macro_f1_4state"]), float(b["macro_f1_4state"]), 0.01, "lower"),
            ("transition_f1", float(c["transition_f1"]), float(b["transition_f1"]), 0.01, "lower"),
            ("false_transitions_per_day", float(c["false_transitions_per_day"]), float(b["false_transitions_per_day"]), 0.05, "higher"),
        )
        for name, new, old, tolerance, direction in checks:
            if direction == "lower" and new < old - tolerance:
                failures.append(f"{symbol}: {name} degraded by more than {tolerance}")
            if direction == "higher" and new > old + tolerance:
                failures.append(f"{symbol}: {name} worsened by more than {tolerance}")
    return {"veto": bool(failures), "failures": failures}


__all__ = [
    "AUXILIARY_C",
    "TemporalBlendCandidate",
    "V5_POLICY",
    "aggregate_fold_metrics",
    "blend_probabilities",
    "candidate_is_promotable",
    "frozen_blend_menu",
    "safety_veto_2025",
    "score_blend_period",
    "select_blend_candidate",
]
