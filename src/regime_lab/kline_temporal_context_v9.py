"""Temporal-context primary classifier for K-line recognizer A (v9).

V9 changes the primary four-state model only. The promoted v5 hysteresis decoder
remains fixed. All temporal inputs are causal summaries of the existing v4
feature family and reset at day/contiguous-run boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp, softmax

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_recognizer_hysteresis_v5 import (
    HysteresisPolicy,
    decoded_events,
    hysteresis_decode,
)
from regime_lab.kline_recognizer_optimization_v4 import (
    CLASS_NAMES,
    CLASS_TO_INT,
    FEATURE_COLUMNS,
    date_mask,
)
from regime_lab.kline_state_recognition import RecognitionConfig
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

V5_POLICY = HysteresisPolicy(0.05, 0.45, 4)


@dataclass(frozen=True, slots=True)
class TemporalContextCandidate:
    horizon: int
    C: float

    def __post_init__(self) -> None:
        if self.horizon not in {3, 6}:
            raise ValueError("horizon outside frozen v9 grid")
        if self.C not in {0.1, 1.0, 10.0}:
            raise ValueError("C outside frozen v9 grid")

    @property
    def candidate_id(self) -> str:
        return f"temporal_h{self.horizon}_C{self.C:g}"

    def to_dict(self) -> dict[str, object]:
        return {"horizon": int(self.horizon), "C": float(self.C)}


def frozen_temporal_menu() -> tuple[TemporalContextCandidate, ...]:
    return tuple(
        TemporalContextCandidate(h, C)
        for h in (3, 6)
        for C in (0.1, 1.0, 10.0)
    )


def temporal_feature_columns(horizon: int) -> tuple[str, ...]:
    if horizon not in {3, 6}:
        raise ValueError("unsupported v9 horizon")
    return tuple(
        [f"cur__{c}" for c in FEATURE_COLUMNS]
        + [f"d1__{c}" for c in FEATURE_COLUMNS]
        + [f"mean{horizon}__{c}" for c in FEATURE_COLUMNS]
        + [f"disp{horizon}__{c}" for c in FEATURE_COLUMNS]
    )


def build_temporal_context(frame: pd.DataFrame, *, horizon: int) -> pd.DataFrame:
    """Build the frozen 48-column causal temporal surface."""
    columns = temporal_feature_columns(horizon)
    required = {
        "symbol",
        "trading_day",
        "contiguous_run_id",
        "market_time_shanghai",
        *FEATURE_COLUMNS,
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"v9 context missing columns: {sorted(missing)}")

    out = pd.DataFrame(np.nan, index=frame.index, columns=columns, dtype=float)
    keys = ["symbol", "trading_day", "contiguous_run_id"]
    for _, group in frame.groupby(keys, sort=False, dropna=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        idx = list(ordered.index)
        if len(idx) < horizon:
            continue
        values = ordered.loc[:, list(FEATURE_COLUMNS)].apply(pd.to_numeric, errors="coerce")
        times = pd.to_datetime(ordered["market_time_shanghai"], errors="raise")
        step_ok = times.diff().eq(pd.Timedelta(minutes=5))
        window_ok = (
            step_ok.astype(int)
            .rolling(horizon - 1, min_periods=horizon - 1)
            .sum()
            .eq(horizon - 1)
        )

        current = values
        d1 = values - values.shift(1)
        mean_h = values.rolling(horizon, min_periods=horizon).mean()
        disp_h = values - values.shift(horizon - 1)
        matrix = np.column_stack(
            [
                current.to_numpy(float),
                d1.to_numpy(float),
                mean_h.to_numpy(float),
                disp_h.to_numpy(float),
            ]
        )
        finite = np.isfinite(matrix).all(axis=1)
        valid = window_ok.to_numpy(bool) & finite
        if valid.any():
            out.loc[np.asarray(idx, dtype=object)[valid], list(columns)] = matrix[valid]
    return out


def temporal_training_arrays(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    candidate: TemporalContextCandidate,
    *,
    start: str | None,
    end: str | None,
) -> tuple[np.ndarray, np.ndarray]:
    cols = temporal_feature_columns(candidate.horizon)
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for symbol in sorted(frames):
        frame = frames[symbol]
        context = contexts[symbol]
        if not context.index.equals(frame.index):
            raise ValueError("v9 context/frame index mismatch")
        values = context.loc[:, list(cols)].to_numpy(float)
        finite = pd.Series(np.isfinite(values).all(axis=1), index=frame.index)
        mask = (
            date_mask(frame, start, end)
            & frame["independent_v3_score_eligible"].fillna(False).astype(bool)
            & frame["independent_judge_available_state"].isin(CLASS_NAMES)
            & finite
        )
        if mask.any():
            xs.append(context.loc[mask, list(cols)].to_numpy(float))
            ys.append(
                frame.loc[mask, "independent_judge_available_state"]
                .map(CLASS_TO_INT)
                .to_numpy(int)
            )
    if not xs:
        raise ValueError("no v9 supervised rows")
    X = np.vstack(xs)
    y = np.concatenate(ys)
    if set(np.unique(y)) != set(range(len(CLASS_NAMES))):
        raise ValueError("all four states required for v9 training")
    return X, y


def fit_temporal_linear(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    candidate: TemporalContextCandidate,
    *,
    start: str | None,
    end: str | None,
) -> dict[str, object]:
    X, y = temporal_training_arrays(frames, contexts, candidate, start=start, end=end)
    mean = np.mean(X, axis=0)
    scale = np.std(X, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
    Z = (X - mean) / scale
    n, d = Z.shape
    k = len(CLASS_NAMES)
    Zb = np.column_stack([np.ones(n), Z])
    counts = np.bincount(y, minlength=k).astype(float)
    sample_weight = (n / (k * counts))[y]
    sample_weight /= float(np.mean(sample_weight))
    weight_sum = float(sample_weight.sum())

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        W = theta.reshape(k, d + 1)
        logits = Zb @ W.T
        log_norm = logsumexp(logits, axis=1)
        loss_rows = log_norm - logits[np.arange(n), y]
        penalty = 0.5 * (1.0 / candidate.C) * float(np.sum(W[:, 1:] ** 2)) / n
        loss = float(np.dot(sample_weight, loss_rows) / weight_sum + penalty)
        probs = np.exp(logits - log_norm[:, None])
        probs[np.arange(n), y] -= 1.0
        probs *= sample_weight[:, None] / weight_sum
        grad = probs.T @ Zb
        grad[:, 1:] += (1.0 / candidate.C) * W[:, 1:] / n
        return loss, grad.ravel()

    result = minimize(
        lambda theta: objective(theta),
        np.zeros(k * (d + 1), dtype=float),
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 300, "ftol": 1e-10, "gtol": 1e-7},
    )
    if not result.success:
        raise RuntimeError(f"v9 linear optimizer failed: {result.message}")
    return {
        "family": "temporal_context_linear",
        "horizon": int(candidate.horizon),
        "C": float(candidate.C),
        "feature_columns": list(temporal_feature_columns(candidate.horizon)),
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "weights": result.x.reshape(k, d + 1).tolist(),
        "optimizer_iterations": int(result.nit),
        "optimizer_loss": float(result.fun),
    }


def temporal_probabilities(context: pd.DataFrame, model: Mapping[str, object]) -> pd.DataFrame:
    cols = tuple(str(c) for c in model["feature_columns"])
    out = pd.DataFrame(np.nan, index=context.index, columns=CLASS_NAMES, dtype=float)
    values = context.loc[:, list(cols)].to_numpy(float)
    finite = np.isfinite(values).all(axis=1)
    if finite.any():
        mean = np.asarray(model["mean"], dtype=float)
        scale = np.asarray(model["scale"], dtype=float)
        weights = np.asarray(model["weights"], dtype=float)
        Z = (values[finite] - mean) / scale
        Zb = np.column_stack([np.ones(len(Z)), Z])
        out.iloc[np.flatnonzero(finite), :] = softmax(Zb @ weights.T, axis=1)
    return out


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_temporal_period(
    frames: Mapping[str, pd.DataFrame],
    contexts: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    model: Mapping[str, object],
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
        probs = temporal_probabilities(context, model)
        decoded = hysteresis_decode(part, probs, V5_POLICY)
        part["v9_prediction"] = decoded
        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v9_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        events = decoded_events(part, decoded, source="v9_temporal_context")
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
        float(aggregate["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"]) + 0.010
        or float(aggregate["min_macro_f1"]) >= float(champion["min_macro_f1"]) + 0.010
        or float(aggregate["min_transition_f1"]) >= float(champion["min_transition_f1"]) + 0.010
        or float(aggregate["max_false_transitions_per_day"])
        <= float(champion["max_false_transitions_per_day"]) - 0.050
    )
    return bool(noninferior and material)


def select_temporal_candidate(
    rows: list[tuple[TemporalContextCandidate, Mapping[str, float]]],
    champion: Mapping[str, float],
) -> tuple[TemporalContextCandidate | None, Mapping[str, float] | None, TemporalContextCandidate | None, Mapping[str, float] | None]:
    eligible = [(c, a) for c, a in rows if candidate_is_promotable(a, champion)]
    point_eligible = [
        (c, a)
        for c, a in rows
        if float(a["min_balanced_accuracy"]) >= float(champion["min_balanced_accuracy"])
        and float(a["min_macro_f1"]) >= float(champion["min_macro_f1"])
    ]
    best = None
    best_agg = None
    if point_eligible:
        best, best_agg = max(
            point_eligible,
            key=lambda item: (
                float(item[1]["min_balanced_accuracy"]),
                float(item[1]["min_macro_f1"]),
                float(item[1]["min_transition_f1"]),
                -float(item[1]["max_false_transitions_per_day"]),
                -int(item[0].horizon),
                -float(item[0].C),
            ),
        )
    if not eligible:
        return None, None, best, best_agg
    selected, aggregate = max(
        eligible,
        key=lambda item: (
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            -int(item[0].horizon),
            -float(item[0].C),
        ),
    )
    return selected, aggregate, best, best_agg


def safety_veto_2025(
    challenger: Mapping[str, Mapping[str, object]],
    champion: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    for symbol in sorted(challenger):
        c = challenger[symbol]
        b = champion[symbol]
        checks = (
            ("balanced_accuracy_4state", 0.030, "lower"),
            ("macro_f1_4state", 0.030, "lower"),
            ("transition_f1", 0.030, "lower"),
            ("false_transitions_per_day", 0.300, "higher"),
        )
        for metric, tolerance, direction in checks:
            cv = float(c[metric])
            bv = float(b[metric])
            bad = cv < bv - tolerance if direction == "lower" else cv > bv + tolerance
            if bad:
                failures.append(f"{symbol}: {metric} catastrophic regression ({cv:.3f} vs {bv:.3f})")
    return {"veto": bool(failures), "failures": failures}


__all__ = [
    "TemporalContextCandidate",
    "aggregate_fold_metrics",
    "build_temporal_context",
    "candidate_is_promotable",
    "fit_temporal_linear",
    "frozen_temporal_menu",
    "safety_veto_2025",
    "score_temporal_period",
    "select_temporal_candidate",
    "temporal_feature_columns",
    "temporal_probabilities",
    "temporal_training_arrays",
]
