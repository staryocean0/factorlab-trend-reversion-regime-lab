"""Strict evaluation for the frozen K-line state recognition v1 study.

This module is deliberately separate from feature/state construction.  It turns
an already-built state timeseries into recognition and transition scores and
ensures that a completely missed concrete class receives F1=0 rather than being
silently omitted from macro-F1.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from regime_lab.kline_state_recognition import (
    ALL_STATES,
    CONCRETE_STATES,
    RecognitionConfig,
    compare_transition_events,
    confirmed_states_and_events,
)


def _safe_f1(precision: float, recall: float, *, supported: bool) -> float:
    if not supported:
        return math.nan
    if math.isfinite(precision) and math.isfinite(recall):
        if precision + recall == 0.0:
            return 0.0
        return 2.0 * precision * recall / (precision + recall)
    # A supported class with no positive predictions has undefined precision but
    # zero recall; scientifically this is a complete miss, so its F1 is zero.
    if math.isfinite(recall) and recall == 0.0:
        return 0.0
    return math.nan


def classification_tables(
    frame: pd.DataFrame,
) -> tuple[dict[str, float | int], pd.DataFrame, pd.DataFrame]:
    """Score concrete oracle states; eligible abstentions count as misses."""
    if "recognition_eligible" in frame.columns:
        eligible = frame["recognition_eligible"].fillna(False).astype(bool)
    else:
        eligible = pd.Series(True, index=frame.index)
    scored = frame.loc[eligible & frame["oracle_state"].isin(CONCRETE_STATES)].copy()
    if scored.empty:
        return {}, pd.DataFrame(), pd.DataFrame()

    y_true = scored["oracle_state"].astype(str)
    y_pred = scored["online_state"].astype(str)
    concrete_pred = y_pred.isin(CONCRETE_STATES)

    confusion = pd.DataFrame(0, index=CONCRETE_STATES, columns=ALL_STATES, dtype=int)
    for truth, prediction in zip(y_true, y_pred, strict=False):
        if truth in confusion.index and prediction in confusion.columns:
            confusion.at[truth, prediction] += 1

    rows: list[dict[str, object]] = []
    recalls: list[float] = []
    f1s: list[float] = []
    for state in CONCRETE_STATES:
        tp = int(((y_true == state) & (y_pred == state)).sum())
        fp = int(((y_true != state) & (y_pred == state)).sum())
        fn = int(((y_true == state) & (y_pred != state)).sum())
        support = int((y_true == state).sum())
        precision = tp / (tp + fp) if tp + fp else math.nan
        recall = tp / (tp + fn) if tp + fn else math.nan
        f1 = _safe_f1(float(precision), float(recall), supported=support > 0)
        if math.isfinite(recall):
            recalls.append(float(recall))
        if math.isfinite(f1):
            f1s.append(float(f1))
        rows.append(
            {
                "state": state,
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": support,
                "predicted_count": int((y_pred == state).sum()),
            }
        )

    summary: dict[str, float | int] = {
        "n_scored": int(len(scored)),
        "online_concrete_coverage": float(concrete_pred.mean()),
        "exact_accuracy_including_abstention": float((y_true == y_pred).mean()),
        "conditional_accuracy_when_online_concrete": (
            float((y_true[concrete_pred] == y_pred[concrete_pred]).mean())
            if concrete_pred.any()
            else math.nan
        ),
        "balanced_accuracy_4state": (
            float(np.mean(recalls)) if len(recalls) == len(CONCRETE_STATES) else math.nan
        ),
        "macro_f1_4state": (
            float(np.mean(f1s)) if len(f1s) == len(CONCRETE_STATES) else math.nan
        ),
    }
    return summary, confusion, pd.DataFrame(rows)


def score_recognition_strict(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[dict[str, object], pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Score point recognition, yearly stability, and confirmed transitions."""
    cfg = config or RecognitionConfig()
    frame = state_timeseries.copy()
    point_summary, confusion, per_state = classification_tables(frame)

    if "recognition_eligible" in frame.columns:
        transition_frame = frame.loc[frame["recognition_eligible"].fillna(False)].copy()
    else:
        transition_frame = frame.copy()

    _, online_events = confirmed_states_and_events(
        transition_frame, label_column="online_state", source="online", config=cfg
    )
    _, oracle_events = confirmed_states_and_events(
        transition_frame, label_column="oracle_state", source="oracle", config=cfg
    )
    transition_table, transition_summary = compare_transition_events(
        online_events,
        oracle_events,
        tolerance_bars=cfg.transition_tolerance_bars,
    )
    days = max(1, transition_frame[["symbol", "trading_day"]].drop_duplicates().shape[0])
    transition_summary["false_transitions_per_day"] = (
        float((transition_table["event_role"].eq("online") & ~transition_table["matched"]).sum()) / days
        if not transition_table.empty
        else 0.0
    )

    yearly_rows: list[dict[str, object]] = []
    years = pd.to_datetime(frame["trading_day"], errors="raise").dt.year
    for year in sorted(years.unique()):
        part = frame.loc[years.eq(year)]
        yearly, _, state_rows = classification_tables(part)
        if not yearly:
            continue
        yearly_rows.append(
            {
                "year": int(year),
                **yearly,
                "min_state_support": int(state_rows["support"].min()) if not state_rows.empty else 0,
            }
        )

    summary: dict[str, object] = {**point_summary, **transition_summary}
    return summary, confusion, per_state, pd.DataFrame(yearly_rows), transition_table


__all__ = ["classification_tables", "score_recognition_strict"]
