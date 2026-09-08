"""Availability-aligned causal state/transition recognition for v2.

V2 does not change the v1 raw recognizer. It applies the already-frozen two-bar
confirmation as a causal persistence decoder and compares that decoded state to
the v1 centered oracle only when the oracle label is actually observable.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from regime_lab.kline_state_evaluation import classification_tables
from regime_lab.kline_state_recognition import (
    ALL_STATES,
    CONCRETE_STATES,
    RecognitionConfig,
    confirmed_states_and_events,
)


V2_ORACLE_AVAILABILITY_LAG_BARS = 6


def _eligible_frame(frame: pd.DataFrame) -> pd.DataFrame:
    if "recognition_eligible" not in frame.columns:
        raise ValueError("recognition_eligible column is required")
    return frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()


def build_v2_state_frame(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
    lag_bars: int = V2_ORACLE_AVAILABILITY_LAG_BARS,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Add decoded online state and availability-aligned confirmed oracle state."""
    cfg = config or RecognitionConfig()
    if lag_bars != cfg.oracle_radius:
        raise ValueError("v2 lag must equal the frozen v1 centered-oracle radius")

    frame = state_timeseries.copy()
    eligible = _eligible_frame(frame)

    online_decoded, online_events = confirmed_states_and_events(
        eligible,
        label_column="online_state",
        source="online_v2",
        config=cfg,
    )
    oracle_confirmed, oracle_center_events = confirmed_states_and_events(
        eligible,
        label_column="oracle_state",
        source="oracle_center_v2",
        config=cfg,
    )

    frame["online_decoded_state"] = "Uncertain"
    frame["oracle_confirmed_center_state"] = "Uncertain"
    frame.loc[eligible.index, "online_decoded_state"] = online_decoded.astype(str)
    frame.loc[eligible.index, "oracle_confirmed_center_state"] = oracle_confirmed.astype(str)
    frame["oracle_available_state"] = pd.NA
    frame["v2_score_eligible"] = False
    frame["eligible_ordinal_day"] = pd.NA

    for (_, _), indices in eligible.groupby(["symbol", "trading_day"], sort=False).groups.items():
        loc = list(indices)
        for ordinal, idx in enumerate(loc):
            frame.at[idx, "eligible_ordinal_day"] = ordinal
            source_ordinal = ordinal - lag_bars
            if source_ordinal < 0:
                continue
            source_idx = loc[source_ordinal]
            frame.at[idx, "oracle_available_state"] = frame.at[
                source_idx, "oracle_confirmed_center_state"
            ]
            frame.at[idx, "v2_score_eligible"] = True

    frame["eligible_ordinal_day"] = pd.to_numeric(
        frame["eligible_ordinal_day"], errors="coerce"
    ).astype("Int64")
    return frame, online_events, oracle_center_events


def classification_for_columns(
    frame: pd.DataFrame,
    *,
    truth_col: str,
    prediction_col: str,
    eligible_col: str,
) -> tuple[dict[str, float | int], pd.DataFrame, pd.DataFrame]:
    """Reuse the strict v1 evaluator on arbitrary v2 truth/prediction columns."""
    missing = {truth_col, prediction_col, eligible_col} - set(frame.columns)
    if missing:
        raise ValueError(f"classification columns missing: {sorted(missing)}")
    view = frame.copy()
    view["oracle_state"] = view[truth_col]
    view["online_state"] = view[prediction_col]
    view["recognition_eligible"] = view[eligible_col].fillna(False).astype(bool)
    return classification_tables(view)


def yearly_classification(
    frame: pd.DataFrame,
    *,
    truth_col: str,
    prediction_col: str,
    eligible_col: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    years = pd.to_datetime(frame["trading_day"], errors="raise").dt.year
    for year in sorted(years.unique()):
        part = frame.loc[years.eq(year)]
        summary, _, per_state = classification_for_columns(
            part,
            truth_col=truth_col,
            prediction_col=prediction_col,
            eligible_col=eligible_col,
        )
        if not summary:
            continue
        rows.append(
            {
                "year": int(year),
                **summary,
                "min_state_support": int(per_state["support"].min()) if not per_state.empty else 0,
            }
        )
    return pd.DataFrame(rows)


def _event_ordinal_maps(frame: pd.DataFrame) -> tuple[dict[tuple[str, str, pd.Timestamp], int], dict[tuple[str, str], list[pd.Timestamp]]]:
    eligible = _eligible_frame(frame)
    lookup: dict[tuple[str, str, pd.Timestamp], int] = {}
    sequences: dict[tuple[str, str], list[pd.Timestamp]] = {}
    for (symbol, day), group in eligible.groupby(["symbol", "trading_day"], sort=False):
        ordered = group.sort_values("market_time_shanghai", kind="stable")
        times = list(ordered["market_time_shanghai"])
        key = (str(symbol), str(day))
        sequences[key] = times
        for ordinal, timestamp in enumerate(times):
            lookup[(str(symbol), str(day), timestamp)] = ordinal
    return lookup, sequences


def compare_availability_aligned_transitions(
    frame: pd.DataFrame,
    online_events: pd.DataFrame,
    oracle_center_events: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
    lag_bars: int = V2_ORACLE_AVAILABILITY_LAG_BARS,
) -> tuple[pd.DataFrame, dict[str, float | int], dict[str, int]]:
    """Score causal transitions against the oracle's true information-availability time."""
    cfg = config or RecognitionConfig()
    if lag_bars != cfg.oracle_radius:
        raise ValueError("v2 transition lag must equal frozen oracle radius")

    lookup, sequences = _event_ordinal_maps(frame)
    online_rows: list[dict[str, object]] = []
    for row in online_events.itertuples(index=False):
        key = (str(row.symbol), str(row.trading_day), row.event_time)
        ordinal = lookup.get(key)
        if ordinal is None:
            continue
        online_rows.append(
            {
                **row._asdict(),
                "eligible_ordinal": int(ordinal),
                "matched": False,
                "match_id": pd.NA,
                "event_role": "online",
            }
        )

    oracle_rows: list[dict[str, object]] = []
    excluded_unavailable = 0
    for row in oracle_center_events.itertuples(index=False):
        event_key = (str(row.symbol), str(row.trading_day), row.event_time)
        center_ordinal = lookup.get(event_key)
        sequence = sequences.get((str(row.symbol), str(row.trading_day)), [])
        if center_ordinal is None:
            continue
        available_ordinal = center_ordinal + lag_bars
        if available_ordinal >= len(sequence):
            excluded_unavailable += 1
            continue
        oracle_rows.append(
            {
                **row._asdict(),
                "oracle_center_eligible_ordinal": int(center_ordinal),
                "oracle_available_eligible_ordinal": int(available_ordinal),
                "oracle_available_event_time": sequence[available_ordinal],
                "matched": False,
                "match_id": pd.NA,
                "event_role": "oracle",
            }
        )

    online = pd.DataFrame(online_rows)
    oracle = pd.DataFrame(oracle_rows)
    match_records: list[dict[str, object]] = []
    match_id = 0

    if not oracle.empty and not online.empty:
        for oi, row in oracle.iterrows():
            candidates = online.loc[
                (~online["matched"])
                & online["symbol"].astype(str).eq(str(row["symbol"]))
                & online["trading_day"].astype(str).eq(str(row["trading_day"]))
                & online["to_state"].astype(str).eq(str(row["to_state"]))
            ].copy()
            if candidates.empty:
                continue
            candidates["distance"] = (
                candidates["eligible_ordinal"]
                - int(row["oracle_available_eligible_ordinal"])
            ).abs()
            candidates = candidates.loc[
                candidates["distance"] <= cfg.transition_tolerance_bars
            ]
            if candidates.empty:
                continue
            best_idx = int(
                candidates.sort_values(["distance", "eligible_ordinal"], kind="stable").index[0]
            )
            match_id += 1
            online.at[best_idx, "matched"] = True
            online.at[best_idx, "match_id"] = match_id
            oracle.at[oi, "matched"] = True
            oracle.at[oi, "match_id"] = match_id
            delay_available = int(
                online.at[best_idx, "eligible_ordinal"]
                - int(row["oracle_available_eligible_ordinal"])
            )
            delay_center = int(
                online.at[best_idx, "eligible_ordinal"]
                - int(row["oracle_center_eligible_ordinal"])
            )
            match_records.append(
                {
                    "match_id": match_id,
                    "symbol": str(row["symbol"]),
                    "trading_day": str(row["trading_day"]),
                    "to_state": str(row["to_state"]),
                    "oracle_center_time": row["event_time"],
                    "oracle_available_time": row["oracle_available_event_time"],
                    "online_time": online.at[best_idx, "event_time"],
                    "delay_vs_availability_bars": delay_available,
                    "delay_vs_availability_minutes": delay_available * 5,
                    "delay_vs_center_bars": delay_center,
                    "delay_vs_center_minutes": delay_center * 5,
                }
            )

    tp = int(online["matched"].sum()) if not online.empty else 0
    fp = int((~online["matched"]).sum()) if not online.empty else 0
    fn = int((~oracle["matched"]).sum()) if not oracle.empty else 0
    precision = tp / (tp + fp) if tp + fp else math.nan
    recall = tp / (tp + fn) if tp + fn else math.nan
    if math.isfinite(precision) and math.isfinite(recall):
        f1 = 0.0 if precision + recall == 0 else 2.0 * precision * recall / (precision + recall)
    else:
        f1 = math.nan

    matches = pd.DataFrame(match_records)
    days = max(1, _eligible_frame(frame)[["symbol", "trading_day"]].drop_duplicates().shape[0])
    summary: dict[str, float | int] = {
        "online_transition_count": int(len(online)),
        "oracle_transition_count": int(len(oracle)),
        "matched_transition_count": tp,
        "transition_precision": float(precision),
        "transition_recall": float(recall),
        "transition_f1": float(f1),
        "false_transitions_per_day": float(fp / days),
        "median_delay_vs_availability_bars": float(matches["delay_vs_availability_bars"].median()) if not matches.empty else math.nan,
        "median_delay_vs_availability_minutes": float(matches["delay_vs_availability_minutes"].median()) if not matches.empty else math.nan,
        "median_delay_vs_center_bars": float(matches["delay_vs_center_bars"].median()) if not matches.empty else math.nan,
        "median_delay_vs_center_minutes": float(matches["delay_vs_center_minutes"].median()) if not matches.empty else math.nan,
    }
    audit = {
        "oracle_center_events_total": int(len(oracle_center_events)),
        "oracle_events_scored": int(len(oracle)),
        "oracle_events_excluded_unavailable_same_day": int(excluded_unavailable),
        "oracle_availability_lag_bars": int(lag_bars),
        "transition_tolerance_bars": int(cfg.transition_tolerance_bars),
    }
    combined = pd.concat([oracle, online], ignore_index=True, sort=False)
    return combined, summary, audit


def v2_score(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[
    dict[str, object],
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, object],
    dict[str, int],
]:
    """Run the frozen v2 point and transition scoring views."""
    cfg = config or RecognitionConfig()
    frame, online_events, oracle_center_events = build_v2_state_frame(
        state_timeseries, config=cfg
    )

    primary_summary, confusion, per_state = classification_for_columns(
        frame,
        truth_col="oracle_available_state",
        prediction_col="online_decoded_state",
        eligible_col="v2_score_eligible",
    )
    yearly = yearly_classification(
        frame,
        truth_col="oracle_available_state",
        prediction_col="online_decoded_state",
        eligible_col="v2_score_eligible",
    )
    transition_table, transition_summary, alignment_audit = compare_availability_aligned_transitions(
        frame,
        online_events,
        oracle_center_events,
        config=cfg,
    )
    summary: dict[str, object] = {**primary_summary, **transition_summary}

    raw_aligned, _, _ = classification_for_columns(
        frame,
        truth_col="oracle_available_state",
        prediction_col="online_state",
        eligible_col="v2_score_eligible",
    )
    decoded_same_center, _, _ = classification_for_columns(
        frame,
        truth_col="oracle_confirmed_center_state",
        prediction_col="online_decoded_state",
        eligible_col="recognition_eligible",
    )
    secondary = {
        "availability_aligned_raw": raw_aligned,
        "same_center_decoded": decoded_same_center,
    }
    return summary, confusion, per_state, yearly, transition_table, secondary, alignment_audit


__all__ = [
    "V2_ORACLE_AVAILABILITY_LAG_BARS",
    "build_v2_state_frame",
    "classification_for_columns",
    "compare_availability_aligned_transitions",
    "v2_score",
    "yearly_classification",
]
