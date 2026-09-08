"""Direct optimization of the K-line recognizer against the frozen v3 benchmark.

V4 intentionally keeps only two roles: one recognizer being improved and the
already-frozen independent v3 judge used as labels/benchmark. 2025 is never
used for feature/model/hyperparameter/confirmation selection.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from typing import Mapping

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import logsumexp

from regime_lab.kline_independent_judge_v3 import compare_independent_transitions
from regime_lab.kline_state_recognition import (
    CONCRETE_STATES,
    RecognitionConfig,
    confirmed_states_and_events,
)
from regime_lab.kline_transition_recognition_v2 import classification_for_columns

FEATURE_COLUMNS = (
    "log_return_1",
    "abs_log_return_1",
    "signed_efficiency_6",
    "signed_efficiency_12",
    "bdci_12",
    "dii_12",
    "realized_volatility_12",
    "volatility_rank_prior480",
    "abs_return_rank_prior480",
    "body_to_range_ratio_6",
    "wick_imbalance_6",
    "close_location_value_6",
)

CLASS_NAMES = tuple(CONCRETE_STATES)
CLASS_TO_INT = {name: i for i, name in enumerate(CLASS_NAMES)}
FAMILY_ORDER = {"rule": 0, "linear": 1, "diagonal_gaussian": 2}


@dataclass(frozen=True, slots=True)
class CandidateConfig:
    family: str
    confirmation_bars: int
    C: float | None = None

    def __post_init__(self) -> None:
        if self.family not in FAMILY_ORDER:
            raise ValueError(f"unknown family: {self.family}")
        if self.confirmation_bars not in {1, 2, 3}:
            raise ValueError("confirmation_bars must be one of {1,2,3}")
        if self.family == "rule":
            if self.confirmation_bars != 2 or self.C is not None:
                raise ValueError("rule baseline is frozen at confirmation=2 and C=None")
        elif self.family == "linear":
            if self.C not in {0.1, 1.0, 10.0}:
                raise ValueError("linear C must be one of {0.1,1.0,10.0}")
        elif self.C is not None:
            raise ValueError("diagonal_gaussian does not use C")

    def to_dict(self) -> dict[str, object]:
        return {
            "family": self.family,
            "confirmation_bars": self.confirmation_bars,
            "C": self.C,
        }


def frozen_candidate_menu() -> tuple[CandidateConfig, ...]:
    rows: list[CandidateConfig] = [CandidateConfig("rule", 2)]
    for C in (0.1, 1.0, 10.0):
        for confirmation in (1, 2, 3):
            rows.append(CandidateConfig("linear", confirmation, C))
    for confirmation in (1, 2, 3):
        rows.append(CandidateConfig("diagonal_gaussian", confirmation))
    return tuple(rows)


def date_mask(frame: pd.DataFrame, start: str | None, end: str | None) -> pd.Series:
    day = pd.to_datetime(frame["trading_day"], errors="raise")
    mask = pd.Series(True, index=frame.index)
    if start is not None:
        mask &= day >= pd.Timestamp(start)
    if end is not None:
        mask &= day <= pd.Timestamp(end)
    return mask


def _finite_feature_mask(frame: pd.DataFrame) -> pd.Series:
    missing = set(FEATURE_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"missing v4 causal features: {sorted(missing)}")
    values = frame.loc[:, FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    return values.notna().all(axis=1) & np.isfinite(values.to_numpy(float)).all(axis=1)


def supervised_mask(frame: pd.DataFrame, start: str | None, end: str | None) -> pd.Series:
    if "independent_v3_score_eligible" not in frame.columns:
        raise ValueError("v3 independent score eligibility is required")
    if "independent_judge_available_state" not in frame.columns:
        raise ValueError("v3 independent available label is required")
    return (
        date_mask(frame, start, end)
        & frame["independent_v3_score_eligible"].fillna(False).astype(bool)
        & frame["independent_judge_available_state"].isin(CLASS_NAMES)
        & _finite_feature_mask(frame)
    )


def training_arrays(
    frames: Mapping[str, pd.DataFrame],
    *,
    start: str | None,
    end: str | None,
) -> tuple[np.ndarray, np.ndarray]:
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    for symbol in sorted(frames):
        frame = frames[symbol]
        mask = supervised_mask(frame, start, end)
        if not mask.any():
            continue
        xs.append(frame.loc[mask, FEATURE_COLUMNS].to_numpy(float))
        ys.append(
            frame.loc[mask, "independent_judge_available_state"]
            .map(CLASS_TO_INT)
            .to_numpy(int)
        )
    if not xs:
        raise ValueError("no supervised rows for requested training interval")
    X = np.vstack(xs)
    y = np.concatenate(ys)
    if set(np.unique(y)) != set(range(len(CLASS_NAMES))):
        raise ValueError("all four concrete classes are required in training data")
    return X, y


def _fit_standardizer(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = np.mean(X, axis=0)
    scale = np.std(X, axis=0)
    scale = np.where(np.isfinite(scale) & (scale > 1e-12), scale, 1.0)
    return mean.astype(float), scale.astype(float)


def _standardize(X: np.ndarray, mean: np.ndarray, scale: np.ndarray) -> np.ndarray:
    return (X - mean) / scale


def fit_linear_model(X: np.ndarray, y: np.ndarray, *, C: float) -> dict[str, object]:
    mean, scale = _fit_standardizer(X)
    Z = _standardize(X, mean, scale)
    n, d = Z.shape
    k = len(CLASS_NAMES)
    Zb = np.column_stack([np.ones(n), Z])
    counts = np.bincount(y, minlength=k).astype(float)
    class_weight = n / (k * counts)
    sample_weight = class_weight[y]
    sample_weight = sample_weight / float(np.mean(sample_weight))
    weight_sum = float(sample_weight.sum())

    def objective(theta: np.ndarray) -> tuple[float, np.ndarray]:
        W = theta.reshape(k, d + 1)
        logits = Zb @ W.T
        log_norm = logsumexp(logits, axis=1)
        loss_rows = log_norm - logits[np.arange(n), y]
        penalty = 0.5 * (1.0 / C) * float(np.sum(W[:, 1:] ** 2)) / n
        loss = float(np.dot(sample_weight, loss_rows) / weight_sum + penalty)

        probs = np.exp(logits - log_norm[:, None])
        probs[np.arange(n), y] -= 1.0
        probs *= sample_weight[:, None] / weight_sum
        grad = probs.T @ Zb
        grad[:, 1:] += (1.0 / C) * W[:, 1:] / n
        return loss, grad.ravel()

    initial = np.zeros(k * (d + 1), dtype=float)
    result = minimize(
        lambda theta: objective(theta),
        initial,
        method="L-BFGS-B",
        jac=True,
        options={"maxiter": 300, "ftol": 1e-10, "gtol": 1e-7},
    )
    if not result.success:
        raise RuntimeError(f"linear optimizer failed: {result.message}")
    return {
        "family": "linear",
        "C": float(C),
        "feature_columns": list(FEATURE_COLUMNS),
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "weights": result.x.reshape(k, d + 1).tolist(),
        "optimizer_iterations": int(result.nit),
        "optimizer_loss": float(result.fun),
    }


def fit_diagonal_gaussian_model(X: np.ndarray, y: np.ndarray) -> dict[str, object]:
    mean, scale = _fit_standardizer(X)
    Z = _standardize(X, mean, scale)
    means: list[list[float]] = []
    variances: list[list[float]] = []
    priors: list[float] = []
    n = len(y)
    for class_id in range(len(CLASS_NAMES)):
        part = Z[y == class_id]
        if part.empty if hasattr(part, "empty") else len(part) == 0:
            raise ValueError("missing class in Gaussian fit")
        means.append(np.mean(part, axis=0).astype(float).tolist())
        var = np.var(part, axis=0)
        variances.append(np.maximum(var, 1e-6).astype(float).tolist())
        priors.append(float(len(part) / n))
    return {
        "family": "diagonal_gaussian",
        "feature_columns": list(FEATURE_COLUMNS),
        "mean": mean.tolist(),
        "scale": scale.tolist(),
        "class_means": means,
        "class_variances": variances,
        "class_priors": priors,
        "variance_floor": 1e-6,
    }


def fit_model(
    frames: Mapping[str, pd.DataFrame],
    config: CandidateConfig,
    *,
    start: str | None,
    end: str | None,
) -> dict[str, object] | None:
    if config.family == "rule":
        return None
    X, y = training_arrays(frames, start=start, end=end)
    if config.family == "linear":
        return fit_linear_model(X, y, C=float(config.C))
    return fit_diagonal_gaussian_model(X, y)


def _predict_fitted(model: Mapping[str, object], X: np.ndarray) -> np.ndarray:
    mean = np.asarray(model["mean"], dtype=float)
    scale = np.asarray(model["scale"], dtype=float)
    Z = _standardize(X, mean, scale)
    family = str(model["family"])
    if family == "linear":
        W = np.asarray(model["weights"], dtype=float)
        Zb = np.column_stack([np.ones(len(Z)), Z])
        score = Zb @ W.T
        return np.argmax(score, axis=1)
    if family == "diagonal_gaussian":
        means = np.asarray(model["class_means"], dtype=float)
        variances = np.asarray(model["class_variances"], dtype=float)
        priors = np.asarray(model["class_priors"], dtype=float)
        scores: list[np.ndarray] = []
        for class_id in range(len(CLASS_NAMES)):
            diff = Z - means[class_id]
            logp = -0.5 * np.sum(np.log(2.0 * math.pi * variances[class_id]) + diff * diff / variances[class_id], axis=1)
            logp += math.log(float(priors[class_id]))
            scores.append(logp)
        return np.argmax(np.column_stack(scores), axis=1)
    raise ValueError(f"unsupported fitted family: {family}")


def raw_predictions(
    frame: pd.DataFrame,
    config: CandidateConfig,
    model: Mapping[str, object] | None,
) -> pd.Series:
    if config.family == "rule":
        return frame["online_state"].astype(object).copy()
    if model is None:
        raise ValueError("fitted family requires model")
    prediction = pd.Series("Uncertain", index=frame.index, dtype=object)
    finite = _finite_feature_mask(frame)
    if finite.any():
        ids = _predict_fitted(model, frame.loc[finite, FEATURE_COLUMNS].to_numpy(float))
        prediction.loc[finite] = [CLASS_NAMES[int(i)] for i in ids]
    return prediction


def decoded_predictions_and_events(
    frame: pd.DataFrame,
    raw: pd.Series,
    *,
    confirmation_bars: int,
    source: str,
) -> tuple[pd.Series, pd.DataFrame]:
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    eligible["_v4_raw_prediction"] = raw.loc[eligible.index].astype(str)
    cfg = replace(RecognitionConfig(), transition_confirm_bars=confirmation_bars)
    decoded, events = confirmed_states_and_events(
        eligible,
        label_column="_v4_raw_prediction",
        source=source,
        config=cfg,
    )
    out = pd.Series("Uncertain", index=frame.index, dtype=object)
    out.loc[eligible.index] = decoded.astype(str)
    return out, events


def _filter_events(events: pd.DataFrame, *, start: str, end: str) -> pd.DataFrame:
    if events.empty:
        return events.copy()
    day = pd.to_datetime(events["trading_day"], errors="raise")
    return events.loc[(day >= pd.Timestamp(start)) & (day <= pd.Timestamp(end))].copy()


def score_config_period(
    frames: Mapping[str, pd.DataFrame],
    judge_events: Mapping[str, pd.DataFrame],
    config: CandidateConfig,
    model: Mapping[str, object] | None,
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
        raw = raw_predictions(part, config, model)
        decoded, online_events = decoded_predictions_and_events(
            part,
            raw,
            confirmation_bars=config.confirmation_bars,
            source=f"v4_{config.family}",
        )
        part["v4_prediction"] = decoded
        point, _, per_state = classification_for_columns(
            part,
            truth_col="independent_judge_available_state",
            prediction_col="v4_prediction",
            eligible_col="independent_v3_score_eligible",
        )
        filtered_judge = _filter_events(judge_events[symbol], start=start, end=end)
        transition_table, transition_summary, _ = compare_independent_transitions(
            part,
            online_events,
            filtered_judge,
            config=RecognitionConfig(),
        )
        results[symbol] = {**point, **transition_summary}
        per_state_tables[symbol] = per_state
        transition_tables[symbol] = transition_table
    return results, per_state_tables, transition_tables


def candidate_selection_key(
    config: CandidateConfig,
    asset_results: Mapping[str, Mapping[str, object]],
) -> tuple[float, float, float, float, int, int, float]:
    symbols = ("000852.SH", "000688.SH")
    min_bal = min(float(asset_results[s]["balanced_accuracy_4state"]) for s in symbols)
    min_macro = min(float(asset_results[s]["macro_f1_4state"]) for s in symbols)
    min_transition = min(float(asset_results[s]["transition_f1"]) for s in symbols)
    mean_false = float(np.mean([float(asset_results[s]["false_transitions_per_day"]) for s in symbols]))
    family_rank = FAMILY_ORDER[config.family]
    c_value = float(config.C) if config.C is not None else 0.0
    return (
        min_bal,
        min_macro,
        min_transition,
        -mean_false,
        -family_rank,
        -config.confirmation_bars,
        -c_value,
    )


def select_candidate(
    rows: list[tuple[CandidateConfig, Mapping[str, Mapping[str, object]]]],
) -> tuple[CandidateConfig, Mapping[str, Mapping[str, object]]]:
    if not rows:
        raise ValueError("candidate rows are empty")
    return max(rows, key=lambda item: candidate_selection_key(item[0], item[1]))


def holdout_success(
    optimized: Mapping[str, Mapping[str, object]],
    baseline: Mapping[str, Mapping[str, object]],
) -> dict[str, object]:
    failures: list[str] = []
    for symbol in ("000852.SH", "000688.SH"):
        row = optimized[symbol]
        base = baseline[symbol]
        gates = {
            "balanced_accuracy_4state": 0.70,
            "macro_f1_4state": 0.70,
            "transition_f1": 0.25,
        }
        for metric, threshold in gates.items():
            value = float(row.get(metric, math.nan))
            if not math.isfinite(value) or value < threshold:
                failures.append(f"{symbol}: {metric} < {threshold:.2f}")
        false_per_day = float(row.get("false_transitions_per_day", math.nan))
        if not math.isfinite(false_per_day) or false_per_day > 0.70:
            failures.append(f"{symbol}: false_transitions_per_day > 0.70")
        bal = float(row.get("balanced_accuracy_4state", math.nan))
        baseline_bal = float(base.get("balanced_accuracy_4state", math.nan))
        if not math.isfinite(bal) or not math.isfinite(baseline_bal) or bal < baseline_bal - 0.03:
            failures.append(f"{symbol}: balanced_accuracy more than 0.03 below same-holdout v3 baseline")
    return {
        "status": "recognizer_improved" if not failures else "recognizer_not_yet_improved",
        "failures": failures,
    }


def serialize_model(model: Mapping[str, object] | None) -> dict[str, object] | None:
    return None if model is None else dict(model)


__all__ = [
    "CandidateConfig",
    "CLASS_NAMES",
    "FEATURE_COLUMNS",
    "candidate_selection_key",
    "date_mask",
    "decoded_predictions_and_events",
    "fit_model",
    "frozen_candidate_menu",
    "holdout_success",
    "raw_predictions",
    "score_config_period",
    "select_candidate",
    "serialize_model",
    "supervised_mask",
    "training_arrays",
]
