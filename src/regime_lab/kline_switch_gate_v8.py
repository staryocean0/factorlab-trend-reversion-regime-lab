"""Learned causal switch gate for the single K-line recognizer A (v8)."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_hysteresis_v5 import (
    HysteresisPolicy,
    linear_probabilities,
    hysteresis_decode,
)
from regime_lab.kline_recognizer_optimization_v4 import (
    CLASS_NAMES,
    FEATURE_COLUMNS,
    date_mask,
)
from regime_lab.kline_state_recognition import RecognitionConfig, confirmed_states_and_events
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

V5_SELECTED_POLICY = HysteresisPolicy(0.05, 0.45, 4)


@dataclass(frozen=True, slots=True)
class SwitchGateCandidate:
    C_gate: float
    threshold: float
    switch_confirm: int
    init_confirm: int = 2

    def __post_init__(self) -> None:
        if self.C_gate not in {0.1, 1.0, 10.0}:
            raise ValueError("C_gate outside frozen v8 grid")
        if self.threshold not in {0.35, 0.50, 0.65}:
            raise ValueError("threshold outside frozen v8 grid")
        if self.switch_confirm not in {1, 2}:
            raise ValueError("switch_confirm outside frozen v8 grid")
        if self.init_confirm != 2:
            raise ValueError("init_confirm is frozen at 2")

    def to_dict(self) -> dict[str, object]:
        return {
            "C_gate": float(self.C_gate),
            "threshold": float(self.threshold),
            "switch_confirm": int(self.switch_confirm),
            "init_confirm": int(self.init_confirm),
        }


def frozen_switch_gate_menu() -> tuple[SwitchGateCandidate, ...]:
    return tuple(
        SwitchGateCandidate(C_gate, threshold, confirm)
        for C_gate in (0.1, 1.0, 10.0)
        for threshold in (0.35, 0.50, 0.65)
        for confirm in (1, 2)
    )


def _v5_reference_state_age(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
) -> tuple[pd.Series, pd.Series]:
    decoded = hysteresis_decode(frame, probabilities, V5_SELECTED_POLICY)
    previous_state = pd.Series(pd.NA, index=frame.index, dtype=object)
    previous_age = pd.Series(np.nan, index=frame.index, dtype=float)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)

    for _, group in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        prior_state: str | None = None
        prior_age = 0
        for idx in ordered.index:
            previous_state.at[idx] = prior_state if prior_state is not None else pd.NA
            previous_age.at[idx] = float(min(prior_age, 20)) if prior_state is not None else math.nan
            state = str(decoded.at[idx])
            if state in CLASS_NAMES:
                if state == prior_state:
                    prior_age += 1
                else:
                    prior_state = state
                    prior_age = 1
            else:
                prior_state = None
                prior_age = 0
    return previous_state, previous_age


def build_switch_feature_frame(
    frame: pd.DataFrame,
    probabilities: pd.DataFrame,
) -> pd.DataFrame:
    if not probabilities.index.equals(frame.index):
        raise ValueError("probability/frame index mismatch")
    if set(CLASS_NAMES) - set(probabilities.columns):
        raise ValueError("missing state probabilities")
    required = {
        "symbol",
        "trading_day",
        "market_time_shanghai",
        "recognition_eligible",
        "contiguous_run_id",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v8 switch feature frame missing columns: {sorted(missing)}")
    feature_missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if feature_missing:
        raise ValueError(f"v8 missing frozen causal features: {sorted(feature_missing)}")

    out = pd.DataFrame(index=frame.index)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)
    previous_state, previous_age = _v5_reference_state_age(frame, probabilities)

    for state in CLASS_NAMES:
        out[f"p_now_{state}"] = pd.to_numeric(probabilities[state], errors="coerce")
        out[f"p_prev_{state}"] = np.nan
        out[f"p_mean3_{state}"] = np.nan

    for _, group in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        idx = list(group.sort_values("market_time_shanghai", kind="stable").index)
        for state in CLASS_NAMES:
            series = probabilities.loc[idx, state].astype(float)
            out.loc[idx, f"p_prev_{state}"] = series.shift(1).to_numpy()
            out.loc[idx, f"p_mean3_{state}"] = series.rolling(3, min_periods=3).mean().to_numpy()

    prob_values = probabilities.loc[:, list(CLASS_NAMES)].to_numpy(float)
    sorted_probs = np.sort(prob_values, axis=1)
    out["top_second_margin"] = sorted_probs[:, -1] - sorted_probs[:, -2]
    proposed_ids = np.argmax(np.where(np.isfinite(prob_values), prob_values, -np.inf), axis=1)
    proposed_states = pd.Series([CLASS_NAMES[int(i)] for i in proposed_ids], index=frame.index, dtype=object)
    proposed_probability = pd.Series(
        [prob_values[i, int(proposed_ids[i])] for i in range(len(frame))],
        index=frame.index,
        dtype=float,
    )

    previous_probability = pd.Series(np.nan, index=frame.index, dtype=float)
    for state in CLASS_NAMES:
        mask = previous_state.astype(object).eq(state)
        previous_probability.loc[mask] = probabilities.loc[mask, state].astype(float)
    out["proposed_minus_v5prev_probability"] = proposed_probability - previous_probability
    out["v5_previous_state_age"] = previous_age.clip(upper=20)
    out["proposed_state"] = proposed_states
    out["v5_previous_state"] = previous_state

    for column in FEATURE_COLUMNS:
        out[column] = pd.to_numeric(frame[column], errors="coerce")
    return out


SWITCH_FEATURE_COLUMNS = tuple(
    [f"p_now_{s}" for s in CLASS_NAMES]
    + [f"p_prev_{s}" for s in CLASS_NAMES]
    + [f"p_mean3_{s}" for s in CLASS_NAMES]
    + ["top_second_margin", "proposed_minus_v5prev_probability", "v5_previous_state_age"]
    + list(FEATURE_COLUMNS)
)


def build_switch_training_rows(
    frame: pd.DataFrame,
    switch_features: pd.DataFrame,
    *,
    start: str | None,
    end: str | None,
) -> tuple[np.ndarray, np.ndarray]:
    date_ok = date_mask(frame, start, end)
    X_rows: list[np.ndarray] = []
    y_rows: list[int] = []
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)
    concrete = frame["independent_judge_available_state"].isin(CLASS_NAMES)
    score_ok = frame["independent_v3_score_eligible"].fillna(False).astype(bool)
    base = frame.loc[date_ok & eligible].copy()

    for _, group in base.groupby(["symbol", "trading_day", "contiguous_run_id"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        indices = list(ordered.index)
        for prev_idx, idx in zip(indices[:-1], indices[1:], strict=False):
            if not (bool(score_ok.at[prev_idx]) and bool(score_ok.at[idx])):
                continue
            if not (bool(concrete.at[prev_idx]) and bool(concrete.at[idx])):
                continue
            prev_time = pd.Timestamp(frame.at[prev_idx, "market_time_shanghai"])
            now_time = pd.Timestamp(frame.at[idx, "market_time_shanghai"])
            if now_time - prev_time != pd.Timedelta(minutes=5):
                continue
            values = switch_features.loc[idx, list(SWITCH_FEATURE_COLUMNS)].to_numpy(dtype=float)
            if not np.isfinite(values).all():
                continue
            prev_label = str(frame.at[prev_idx, "independent_judge_available_state"])
            now_label = str(frame.at[idx, "independent_judge_available_state"])
            X_rows.append(values)
            y_rows.append(int(now_label != prev_label))

    if not X_rows:
        raise ValueError("no v8 switch-gate training rows")
    X = np.vstack(X_rows)
    y = np.asarray(y_rows, dtype=int)
    if set(np.unique(y)) != {0, 1}:
        raise ValueError("v8 switch-gate training requires both classes")
    return X, y


def fit_switch_gate(X: np.ndarray, y: np.ndarray, *, C_gate: float) -> dict[str, object]:
    mean = np.mean(X, axis=0)
    scale = np.std(X, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
    Z = (X - mean) / scale
    Zb = np.column_stack([np.ones(len(Z)), Z])
    counts = np.bincount(y, minlength=2).astype(float)
    sample_weight = len(y) / (2.0 * counts[y])
    sample_weight /= float(np.mean(sample_weight))
    weight_sum = float(sample_weight.sum())

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        logits = Zb @ theta
        probs = expit(logits)
        eps = 1e-12
        loss_rows = -(y * np.log(probs + eps) + (1 - y) * np.log(1.0 - probs + eps))
        penalty = 0.5 * (1.0 / C_gate) * float(np.sum(theta[1:] ** 2)) / len(y)
        loss = float(np.dot(sample_weight, loss_rows) / weight_sum + penalty)
        residual = (probs - y) * sample_weight / weight_sum
        grad = Zb.T @ residual
        grad[1:] += (1.0 / C_gate) * theta[1:] / len(y)
        return loss, grad

    result = minimize(
        lambda theta: objective(theta),
        np.zeros(Zb.shape[1], dtype=float),
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 300, "ftol": 1e-10, "gtol": 1e-7},
    )
    if not result.success:
        raise RuntimeError(f"v8 switch-gate optimizer failed: {result.message}")
    return {
        "family": "binary_logistic_switch_gate",
        "C_gate": float(C_gate),
        "feature_columns": list(SWITCH_FEATURE_COLUMNS),
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "weights": result.x.tolist(),
        "positive_rate": float(np.mean(y)),
        "optimizer_iterations": int(result.nit),
        "optimizer_loss": float(result.fun),
    }


def switch_gate_probabilities(
    switch_features: pd.DataFrame,
    model: Mapping[str, object],
) -> pd.Series:
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    weights = np.asarray(model["weights"], dtype=float)
    out = pd.Series(np.nan, index=switch_features.index, dtype=float)
    values = switch_features.loc[:, list(SWITCH_FEATURE_COLUMNS)].to_numpy(float)
    finite = np.isfinite(values).all(axis=1)
    if finite.any():
        Z = (values[finite] - mean) / scale
        Zb = np.column_stack([np.ones(len(Z)), Z])
        out.iloc[np.flatnonzero(finite)] = expit(Zb @ weights)
    return out


def switch_gate_decode(
    frame: pd.DataFrame,
    state_probabilities: pd.DataFrame,
    gate_probabilities: pd.Series,
    candidate: SwitchGateCandidate,
) -> pd.Series:
    decoded = pd.Series("Uncertain", index=frame.index, dtype=object)
    eligible = frame["recognition_eligible"].fillna(False).astype(bool)
    for _, group in frame.loc[eligible].groupby(["symbol", "trading_day"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        current: str | None = None
        init_pending: str | None = None
        init_count = 0
        switch_pending: str | None = None
        switch_count = 0
        for idx in ordered.index:
            probs = state_probabilities.loc[idx, list(CLASS_NAMES)].to_numpy(float)
            if not np.isfinite(probs).all():
                if current is not None:
                    decoded.at[idx] = current
                continue
            proposed = str(CLASS_NAMES[int(np.argmax(probs))])
            if current is None:
                if init_pending == proposed:
                    init_count += 1
                else:
                    init_pending = proposed
                    init_count = 1
                if init_count >= candidate.init_confirm:
                    current = proposed
                    init_pending = None
                    init_count = 0
                if current is not None:
                    decoded.at[idx] = current
                continue

            if proposed == current:
                switch_pending = None
                switch_count = 0
                decoded.at[idx] = current
                continue

            gate = float(gate_probabilities.at[idx]) if pd.notna(gate_probabilities.at[idx]) else math.nan
            if math.isfinite(gate) and gate >= candidate.threshold:
                if switch_pending == proposed:
                    switch_count += 1
                else:
                    switch_pending = proposed
                    switch_count = 1
                if switch_count >= candidate.switch_confirm:
                    current = proposed
                    switch_pending = None
                    switch_count = 0
            else:
                switch_pending = None
                switch_count = 0
            decoded.at[idx] = current
    return decoded


def decoded_events(frame: pd.DataFrame, decoded: pd.Series, *, source: str) -> pd.DataFrame:
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    eligible["_v8_state"] = decoded.loc[eligible.index].astype(str)
    cfg = replace(RecognitionConfig(), transition_confirm_bars=1)
    _, events = confirmed_states_and_events(
        eligible,
        label_column="_v8_state",
        source=source,
        config=cfg,
    )
    return events


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_switch_gate_period(
    frames: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    state_models: Mapping[str, Mapping[str, object]],
    gate_model: Mapping[str, object],
    candidate: SwitchGateCandidate,
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
        probs = linear_probabilities(part, state_models[symbol])
        switch_features = build_switch_feature_frame(part, probs)
        gate_probs = switch_gate_probabilities(switch_features, gate_model)
        decoded = switch_gate_decode(part, probs, gate_probs, candidate)
        part["v8_prediction"] = decoded
        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v8_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v8_switch_gate")
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
        "min_balanced_accuracy": min(float(c["balanced_accuracy_4state"]) for c in cells),
        "min_macro_f1": min(float(c["macro_f1_4state"]) for c in cells),
        "min_transition_f1": min(float(c["transition_f1"]) for c in cells),
        "max_false_transitions_per_day": max(float(c["false_transitions_per_day"]) for c in cells),
        "mean_false_transitions_per_day": float(np.mean([float(c["false_transitions_per_day"]) for c in cells])),
    }


def candidate_point_eligible(aggregate: Mapping[str, float]) -> bool:
    return (
        float(aggregate["min_balanced_accuracy"]) >= 0.75
        and float(aggregate["min_macro_f1"]) >= 0.72
    )


def candidate_promotable(
    aggregate: Mapping[str, float],
    v5_aggregate: Mapping[str, float],
) -> bool:
    if not candidate_point_eligible(aggregate):
        return False
    transition = float(aggregate["min_transition_f1"])
    false_day = float(aggregate["max_false_transitions_per_day"])
    v5_transition = float(v5_aggregate["min_transition_f1"])
    v5_false = float(v5_aggregate["max_false_transitions_per_day"])
    if transition < v5_transition or false_day > v5_false:
        return False
    return (transition - v5_transition >= 0.01) or (v5_false - false_day >= 0.05)


def candidate_selection_key(
    candidate: SwitchGateCandidate,
    aggregate: Mapping[str, float],
) -> tuple[float, float, float, float, int, float, float]:
    return (
        float(aggregate["min_transition_f1"]),
        -float(aggregate["max_false_transitions_per_day"]),
        float(aggregate["min_balanced_accuracy"]),
        float(aggregate["min_macro_f1"]),
        -int(candidate.switch_confirm),
        float(candidate.threshold),
        -float(candidate.C_gate),
    )


def select_switch_gate_candidate(
    rows: list[tuple[SwitchGateCandidate, Mapping[str, float]]],
    v5_aggregate: Mapping[str, float],
) -> tuple[SwitchGateCandidate | None, Mapping[str, float] | None]:
    promotable = [item for item in rows if candidate_promotable(item[1], v5_aggregate)]
    if not promotable:
        return None, None
    return max(promotable, key=lambda item: candidate_selection_key(item[0], item[1]))


def diagnostic_success(
    selected: Mapping[str, Mapping[str, object]],
    v5: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    strong_failures: list[str] = []
    for symbol in ("000852.SH", "000688.SH"):
        s = selected[symbol]
        b = v5[symbol]
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
        "useful_improvement": not failures,
        "useful_failures": failures,
        "strong_target_passed": not strong_failures,
        "strong_failures": strong_failures,
    }


__all__ = [
    "SWITCH_FEATURE_COLUMNS",
    "SwitchGateCandidate",
    "V5_SELECTED_POLICY",
    "aggregate_fold_metrics",
    "build_switch_feature_frame",
    "build_switch_training_rows",
    "candidate_point_eligible",
    "candidate_promotable",
    "diagnostic_success",
    "fit_switch_gate",
    "frozen_switch_gate_menu",
    "score_switch_gate_period",
    "select_switch_gate_candidate",
    "switch_gate_decode",
    "switch_gate_probabilities",
]
