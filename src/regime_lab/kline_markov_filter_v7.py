"""Causal Markov persistence filter for the single K-line recognizer A.

V7 keeps the locked linear classifier and frozen v3 benchmark unchanged. It
learns only a pooled four-state transition matrix from pre-validation labels and
uses online forward filtering; no backward smoothing or future information.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Mapping

import numpy as np
import pandas as pd

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_optimization_v4 import CLASS_NAMES, date_mask
from regime_lab.kline_state_recognition import RecognitionConfig, confirmed_states_and_events
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

CLASS_TO_INT = {name: idx for idx, name in enumerate(CLASS_NAMES)}


@dataclass(frozen=True, slots=True)
class MarkovCandidate:
    eta: float
    beta: float

    def __post_init__(self) -> None:
        if self.eta not in {0.5, 1.0, 2.0, 4.0}:
            raise ValueError("eta outside frozen v7 grid")
        if self.beta not in {0.5, 1.0, 2.0}:
            raise ValueError("beta outside frozen v7 grid")

    @property
    def candidate_id(self) -> str:
        return f"markov_eta{self.eta:g}_beta{self.beta:g}"

    def to_dict(self) -> dict[str, float]:
        return {"eta": float(self.eta), "beta": float(self.beta)}


def frozen_markov_menu() -> tuple[MarkovCandidate, ...]:
    return tuple(
        MarkovCandidate(eta, beta)
        for eta in (0.5, 1.0, 2.0, 4.0)
        for beta in (0.5, 1.0, 2.0)
    )


def fit_markov_state_model(
    frames: Mapping[str, pd.DataFrame],
    *,
    start: str | None,
    end: str | None,
    pseudocount: float = 1.0,
) -> dict[str, object]:
    if pseudocount != 1.0:
        raise ValueError("v7 pseudocount is frozen at 1.0")
    k = len(CLASS_NAMES)
    transition_counts = np.full((k, k), pseudocount, dtype=float)
    prior_counts = np.full(k, pseudocount, dtype=float)
    observed_pairs = 0
    observed_labels = 0

    for symbol in sorted(frames):
        frame = frames[symbol]
        required = {
            "symbol",
            "trading_day",
            "market_time_shanghai",
            "independent_v3_score_eligible",
            "independent_judge_available_state",
        }
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"v7 Markov training columns missing: {sorted(missing)}")
        mask = date_mask(frame, start, end)
        part = frame.loc[mask].copy()
        part = part.loc[
            part["independent_v3_score_eligible"].fillna(False).astype(bool)
            & part["independent_judge_available_state"].isin(CLASS_NAMES)
        ].copy()
        if part.empty:
            continue

        for label in part["independent_judge_available_state"].astype(str):
            prior_counts[CLASS_TO_INT[label]] += 1.0
            observed_labels += 1

        for _, day in part.groupby(["symbol", "trading_day"], sort=False):
            ordered = day.sort_values("market_time_shanghai", kind="stable")
            rows = list(ordered.itertuples(index=False))
            if len(rows) < 2:
                continue
            for left, right in zip(rows[:-1], rows[1:], strict=False):
                consecutive = True
                if hasattr(left, "eligible_ordinal_day_v3") and hasattr(right, "eligible_ordinal_day_v3"):
                    lo = getattr(left, "eligible_ordinal_day_v3")
                    ro = getattr(right, "eligible_ordinal_day_v3")
                    if pd.notna(lo) and pd.notna(ro):
                        consecutive = int(ro) - int(lo) == 1
                if not consecutive:
                    continue
                a = CLASS_TO_INT[str(left.independent_judge_available_state)]
                b = CLASS_TO_INT[str(right.independent_judge_available_state)]
                transition_counts[a, b] += 1.0
                observed_pairs += 1

    if observed_labels <= 0 or observed_pairs <= 0:
        raise ValueError("insufficient concrete pre-validation labels for v7 Markov fit")

    transition = transition_counts / transition_counts.sum(axis=1, keepdims=True)
    prior = prior_counts / prior_counts.sum()
    return {
        "class_names": list(CLASS_NAMES),
        "transition_counts": transition_counts.tolist(),
        "transition_matrix": transition.tolist(),
        "prior_counts": prior_counts.tolist(),
        "prior": prior.tolist(),
        "observed_labels": int(observed_labels),
        "observed_transition_pairs": int(observed_pairs),
        "pseudocount": float(pseudocount),
    }


def sharpen_transition_matrix(matrix: np.ndarray, eta: float) -> np.ndarray:
    values = np.asarray(matrix, dtype=float)
    if values.shape != (len(CLASS_NAMES), len(CLASS_NAMES)):
        raise ValueError("v7 transition matrix must be 4x4")
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("v7 transition matrix must contain finite positive probabilities")
    powered = np.power(values, float(eta))
    return powered / powered.sum(axis=1, keepdims=True)


def markov_filter_decode(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
    markov_model: Mapping[str, object],
    candidate: MarkovCandidate,
) -> pd.Series:
    if not probabilities.index.equals(frame.index):
        raise ValueError("v7 probability/frame index mismatch")
    if set(CLASS_NAMES) - set(probabilities.columns):
        raise ValueError("v7 missing class probabilities")
    required = {"symbol", "trading_day", "market_time_shanghai", "recognition_eligible"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v7 decoder columns missing: {sorted(missing)}")

    transition = sharpen_transition_matrix(
        np.asarray(markov_model["transition_matrix"], dtype=float), candidate.eta
    )
    prior = np.asarray(markov_model["prior"], dtype=float)
    if prior.shape != (len(CLASS_NAMES),) or not np.isfinite(prior).all() or (prior <= 0).any():
        raise ValueError("invalid v7 prior")
    prior = prior / prior.sum()

    decoded = pd.Series("Uncertain", index=frame.index, dtype=object)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)

    for _, day in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        ordered = day.sort_values("market_time_shanghai", kind="stable")
        posterior: np.ndarray | None = None
        for idx in ordered.index:
            emission = probabilities.loc[idx, list(CLASS_NAMES)].to_numpy(float)
            if not np.isfinite(emission).all() or (emission < 0).any() or float(emission.sum()) <= 0.0:
                if posterior is not None:
                    decoded.at[idx] = str(CLASS_NAMES[int(np.argmax(posterior))])
                continue
            emission = emission / emission.sum()
            emission_term = np.power(np.maximum(emission, 1e-15), candidate.beta)
            predictive = prior if posterior is None else posterior @ transition
            posterior = predictive * emission_term
            total = float(posterior.sum())
            if not math.isfinite(total) or total <= 0.0:
                raise RuntimeError("v7 posterior normalization failed")
            posterior = posterior / total
            decoded.at[idx] = str(CLASS_NAMES[int(np.argmax(posterior))])
    return decoded


def decoded_events(frame: pd.DataFrame, decoded: pd.Series, *, source: str) -> pd.DataFrame:
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    eligible["_v7_state"] = decoded.loc[eligible.index].astype(str)
    cfg = replace(RecognitionConfig(), transition_confirm_bars=1)
    _, events = confirmed_states_and_events(
        eligible,
        label_column="_v7_state",
        source=source,
        config=cfg,
    )
    return events


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_markov_period_from_probabilities(
    frames: Mapping[str, pd.DataFrame],
    probabilities: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    markov_model: Mapping[str, object],
    candidate: MarkovCandidate,
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
        decoded = markov_filter_decode(part, probs, markov_model, candidate)
        part["v7_prediction"] = decoded
        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v7_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source=f"v7_{candidate.candidate_id}")
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
        "min_balanced_accuracy": min(float(cell["balanced_accuracy_4state"]) for cell in cells),
        "min_macro_f1": min(float(cell["macro_f1_4state"]) for cell in cells),
        "min_transition_f1": min(float(cell["transition_f1"]) for cell in cells),
        "max_false_transitions_per_day": max(float(cell["false_transitions_per_day"]) for cell in cells),
        "mean_false_transitions_per_day": float(
            np.mean([float(cell["false_transitions_per_day"]) for cell in cells])
        ),
    }


def markov_point_eligible(aggregate: Mapping[str, float]) -> bool:
    return (
        float(aggregate["min_balanced_accuracy"]) >= 0.75
        and float(aggregate["min_macro_f1"]) >= 0.72
    )


def markov_promotable(
    aggregate: Mapping[str, float],
    baseline: Mapping[str, float],
) -> bool:
    if not markov_point_eligible(aggregate):
        return False
    transition = float(aggregate["min_transition_f1"])
    false_rate = float(aggregate["max_false_transitions_per_day"])
    base_transition = float(baseline["min_transition_f1"])
    base_false = float(baseline["max_false_transitions_per_day"])
    no_worse = transition >= base_transition and false_rate <= base_false
    material = transition >= base_transition + 0.01 or false_rate <= base_false - 0.05
    return bool(no_worse and material)


def markov_selection_key(
    candidate: MarkovCandidate,
    aggregate: Mapping[str, float],
) -> tuple[float, float, float, float, float, float]:
    return (
        float(aggregate["min_transition_f1"]),
        -float(aggregate["max_false_transitions_per_day"]),
        float(aggregate["min_balanced_accuracy"]),
        float(aggregate["min_macro_f1"]),
        -float(candidate.eta),
        -float(candidate.beta),
    )


def select_markov_candidate(
    rows: list[tuple[MarkovCandidate, Mapping[str, float]]],
    baseline_aggregate: Mapping[str, float],
) -> tuple[MarkovCandidate | None, Mapping[str, float] | None, MarkovCandidate | None, Mapping[str, float] | None]:
    if not rows:
        raise ValueError("v7 Markov candidate rows are empty")
    point_eligible = [(c, a) for c, a in rows if markov_point_eligible(a)]
    best = max(point_eligible, key=lambda item: markov_selection_key(item[0], item[1])) if point_eligible else None
    promotable = [(c, a) for c, a in rows if markov_promotable(a, baseline_aggregate)]
    selected = max(promotable, key=lambda item: markov_selection_key(item[0], item[1])) if promotable else None
    return (
        selected[0] if selected else None,
        selected[1] if selected else None,
        best[0] if best else None,
        best[1] if best else None,
    )


def diagnostic_success(
    selected: Mapping[str, Mapping[str, object]],
    baseline: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    strong_failures: list[str] = []
    for symbol in ("000852.SH", "000688.SH"):
        s = selected[symbol]
        b = baseline[symbol]
        if float(s["transition_f1"]) < float(b["transition_f1"]):
            failures.append(f"{symbol}: transition_f1 below v5")
        if float(s["false_transitions_per_day"]) > float(b["false_transitions_per_day"]):
            failures.append(f"{symbol}: false_transitions_per_day above v5")
        if float(s["balanced_accuracy_4state"]) < 0.75:
            failures.append(f"{symbol}: balanced_accuracy < 0.75")
        if float(s["macro_f1_4state"]) < 0.72:
            failures.append(f"{symbol}: macro_f1 < 0.72")
        if float(s["transition_f1"]) < 0.30:
            strong_failures.append(f"{symbol}: transition_f1 < 0.30")
        if float(s["false_transitions_per_day"]) > 0.80:
            strong_failures.append(f"{symbol}: false_transitions_per_day > 0.80")
    return {
        "status": "useful_v7_improvement" if not failures else "v7_not_yet_useful",
        "failures": failures,
        "strong_target_passed": not strong_failures,
        "strong_target_failures": strong_failures,
    }


__all__ = [
    "MarkovCandidate",
    "aggregate_fold_metrics",
    "decoded_events",
    "diagnostic_success",
    "fit_markov_state_model",
    "frozen_markov_menu",
    "markov_filter_decode",
    "markov_point_eligible",
    "markov_promotable",
    "markov_selection_key",
    "score_markov_period_from_probabilities",
    "select_markov_candidate",
    "sharpen_transition_matrix",
]
