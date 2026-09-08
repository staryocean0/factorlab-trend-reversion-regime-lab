"""Independent geometric judge for K-line recognition v3.

The judge is deliberately formula-separated from the v1/v2 recognizer. It uses
centered OHLC geometry for offline evaluation only. Online state construction
remains unchanged and strictly causal.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right, insort
from collections import deque
import math

import numpy as np
import pandas as pd

from regime_lab.kline_state_recognition import (
    ALL_STATES,
    CONCRETE_STATES,
    RecognitionConfig,
    confirmed_states_and_events,
)
from regime_lab.kline_transition_recognition_v2 import (
    classification_for_columns,
    yearly_classification,
)

INDEPENDENT_JUDGE_RADIUS = 8
INDEPENDENT_JUDGE_WINDOW = 17
INDEPENDENT_REFERENCE_HISTORY = 480


def _causal_rank_against_reference(
    current: pd.Series,
    reference: pd.Series,
    *,
    history: int = INDEPENDENT_REFERENCE_HISTORY,
) -> pd.Series:
    cur = pd.to_numeric(current, errors="coerce").to_numpy(float)
    ref = pd.to_numeric(reference, errors="coerce").to_numpy(float)
    out = np.full(len(cur), np.nan, dtype=float)
    queue: deque[float] = deque()
    ordered: list[float] = []
    for i in range(len(cur)):
        value = cur[i]
        if math.isfinite(value) and len(queue) >= history:
            out[i] = bisect_right(ordered, float(value)) / float(len(ordered))
        reference_value = ref[i]
        if math.isfinite(reference_value):
            reference_value = float(reference_value)
            queue.append(reference_value)
            insort(ordered, reference_value)
            if len(queue) > history:
                old = queue.popleft()
                ordered.pop(bisect_left(ordered, old))
    return pd.Series(out, index=current.index, dtype="float64")


def _linear_r(log_close: np.ndarray) -> float:
    y = np.asarray(log_close, dtype=float)
    if len(y) < 3 or not np.isfinite(y).all() or float(np.std(y)) <= 0.0:
        return 0.0
    x = np.arange(len(y), dtype=float)
    value = float(np.corrcoef(x, y)[0, 1])
    return value if math.isfinite(value) else 0.0


def _turning_point_density(close: np.ndarray) -> float:
    values = np.asarray(close, dtype=float)
    if len(values) < 3:
        return math.nan
    left = values[1:-1] - values[:-2]
    right = values[2:] - values[1:-1]
    turning = ((left > 0) & (right < 0)) | ((left < 0) & (right > 0))
    return float(np.mean(turning))


def classify_independent_geometry(
    *,
    linear_r: float,
    channel_displacement: float,
    terminal_channel_location: float,
    turning_point_density: float,
    median_range_rank: float,
    max_range_rank: float,
) -> str:
    required = (
        linear_r,
        channel_displacement,
        terminal_channel_location,
        turning_point_density,
        median_range_rank,
        max_range_rank,
    )
    if not all(math.isfinite(float(value)) for value in required):
        return "Uncertain"
    if median_range_rank >= 0.95 or max_range_rank >= 0.995:
        return "Shock"
    if (
        linear_r >= 0.70
        and channel_displacement >= 0.40
        and terminal_channel_location >= 0.70
        and turning_point_density <= 0.45
    ):
        return "UpTrend"
    if (
        linear_r <= -0.70
        and channel_displacement <= -0.40
        and terminal_channel_location <= 0.30
        and turning_point_density <= 0.45
    ):
        return "DownTrend"
    if (
        abs(linear_r) <= 0.40
        and abs(channel_displacement) <= 0.30
        and turning_point_density >= 0.35
    ):
        return "Range"
    return "Uncertain"


def _centered_geometry(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    columns = [
        "independent_linear_r",
        "independent_channel_displacement",
        "independent_terminal_channel_location",
        "independent_turning_point_density",
        "independent_centered_median_log_range",
        "independent_centered_max_log_range",
    ]
    for column in columns:
        out[column] = np.nan

    for _, group in out.groupby(["symbol", "contiguous_run_id"], sort=False):
        indices = list(group.index)
        if len(indices) < INDEPENDENT_JUDGE_WINDOW:
            continue
        for position in range(INDEPENDENT_JUDGE_RADIUS, len(indices) - INDEPENDENT_JUDGE_RADIUS):
            center_idx = indices[position]
            window_idx = indices[
                position - INDEPENDENT_JUDGE_RADIUS : position + INDEPENDENT_JUDGE_RADIUS + 1
            ]
            part = out.loc[window_idx]
            close = part["close"].to_numpy(float)
            high = part["high"].to_numpy(float)
            low = part["low"].to_numpy(float)
            log_close = np.log(close)
            channel_low = float(np.min(low))
            channel_high = float(np.max(high))
            width = channel_high - channel_low
            if width <= 0.0:
                displacement = 0.0
                terminal = 0.5
            else:
                displacement = float((close[-1] - close[0]) / width)
                terminal = float((close[-1] - channel_low) / width)
            log_range = np.log(high / low)
            out.at[center_idx, "independent_linear_r"] = _linear_r(log_close)
            out.at[center_idx, "independent_channel_displacement"] = displacement
            out.at[center_idx, "independent_terminal_channel_location"] = terminal
            out.at[center_idx, "independent_turning_point_density"] = _turning_point_density(close)
            out.at[center_idx, "independent_centered_median_log_range"] = float(np.median(log_range))
            out.at[center_idx, "independent_centered_max_log_range"] = float(np.max(log_range))
    return out


def build_independent_judge_frame(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build independent centered judge labels and the unchanged v2 causal decoder."""
    cfg = config or RecognitionConfig()
    required = {
        "symbol",
        "trading_day",
        "market_time_shanghai",
        "open",
        "high",
        "low",
        "close",
        "contiguous_run_id",
        "recognition_eligible",
        "online_state",
    }
    missing = required - set(state_timeseries.columns)
    if missing:
        raise ValueError(f"independent judge frame missing columns: {sorted(missing)}")

    frame = _centered_geometry(state_timeseries.copy())
    frame["_bar_log_range"] = np.log(frame["high"].astype(float) / frame["low"].astype(float))
    frame["_trailing_median_range17"] = np.nan
    frame["_trailing_max_range17"] = np.nan
    for _, indices in frame.groupby(["symbol", "contiguous_run_id"], sort=False).groups.items():
        loc = list(indices)
        ranges = frame.loc[loc, "_bar_log_range"]
        frame.loc[loc, "_trailing_median_range17"] = ranges.rolling(
            INDEPENDENT_JUDGE_WINDOW, min_periods=INDEPENDENT_JUDGE_WINDOW
        ).median().to_numpy()
        frame.loc[loc, "_trailing_max_range17"] = ranges.rolling(
            INDEPENDENT_JUDGE_WINDOW, min_periods=INDEPENDENT_JUDGE_WINDOW
        ).max().to_numpy()

    frame["independent_median_range_rank_prior480"] = np.nan
    frame["independent_max_range_rank_prior480"] = np.nan
    for _, indices in frame.groupby("symbol", sort=False).groups.items():
        loc = list(indices)
        frame.loc[loc, "independent_median_range_rank_prior480"] = _causal_rank_against_reference(
            frame.loc[loc, "independent_centered_median_log_range"],
            frame.loc[loc, "_trailing_median_range17"],
        ).to_numpy()
        frame.loc[loc, "independent_max_range_rank_prior480"] = _causal_rank_against_reference(
            frame.loc[loc, "independent_centered_max_log_range"],
            frame.loc[loc, "_trailing_max_range17"],
        ).to_numpy()

    frame["independent_judge_center_state"] = [
        classify_independent_geometry(
            linear_r=float(r) if pd.notna(r) else math.nan,
            channel_displacement=float(d) if pd.notna(d) else math.nan,
            terminal_channel_location=float(t) if pd.notna(t) else math.nan,
            turning_point_density=float(tp) if pd.notna(tp) else math.nan,
            median_range_rank=float(mr) if pd.notna(mr) else math.nan,
            max_range_rank=float(xr) if pd.notna(xr) else math.nan,
        )
        for r, d, t, tp, mr, xr in zip(
            frame["independent_linear_r"],
            frame["independent_channel_displacement"],
            frame["independent_terminal_channel_location"],
            frame["independent_turning_point_density"],
            frame["independent_median_range_rank_prior480"],
            frame["independent_max_range_rank_prior480"],
            strict=False,
        )
    ]
    metric_columns = [
        "independent_linear_r",
        "independent_channel_displacement",
        "independent_terminal_channel_location",
        "independent_turning_point_density",
        "independent_median_range_rank_prior480",
        "independent_max_range_rank_prior480",
    ]
    frame["independent_judge_center_eligible"] = frame[metric_columns].notna().all(axis=1)

    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
    decoded, online_events = confirmed_states_and_events(
        eligible,
        label_column="online_state",
        source="online_v3",
        config=cfg,
    )
    frame["online_decoded_state_v3"] = "Uncertain"
    frame.loc[eligible.index, "online_decoded_state_v3"] = decoded.astype(str)

    judge_event_frame = frame.loc[
        frame["independent_judge_center_eligible"] & frame["recognition_eligible"].fillna(False)
    ].copy()
    _, judge_center_events = confirmed_states_and_events(
        judge_event_frame,
        label_column="independent_judge_center_state",
        source="independent_judge_center_v3",
        config=cfg,
    )

    frame["independent_judge_available_state"] = pd.NA
    frame["independent_v3_score_eligible"] = False
    frame["eligible_ordinal_day_v3"] = pd.NA
    for (_, _), indices in eligible.groupby(["symbol", "trading_day"], sort=False).groups.items():
        loc = list(indices)
        for ordinal, idx in enumerate(loc):
            frame.at[idx, "eligible_ordinal_day_v3"] = ordinal
            source_ordinal = ordinal - INDEPENDENT_JUDGE_RADIUS
            if source_ordinal < 0:
                continue
            source_idx = loc[source_ordinal]
            if not bool(frame.at[source_idx, "independent_judge_center_eligible"]):
                continue
            frame.at[idx, "independent_judge_available_state"] = frame.at[
                source_idx, "independent_judge_center_state"
            ]
            frame.at[idx, "independent_v3_score_eligible"] = True
    frame["eligible_ordinal_day_v3"] = pd.to_numeric(
        frame["eligible_ordinal_day_v3"], errors="coerce"
    ).astype("Int64")
    return frame, online_events, judge_center_events


def _event_maps(frame: pd.DataFrame) -> tuple[dict[tuple[str, str, pd.Timestamp], int], dict[tuple[str, str], list[pd.Timestamp]]]:
    eligible = frame.loc[frame["recognition_eligible"].fillna(False).astype(bool)].copy()
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


def compare_independent_transitions(
    frame: pd.DataFrame,
    online_events: pd.DataFrame,
    judge_center_events: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, float | int], dict[str, int]]:
    cfg = config or RecognitionConfig()
    lookup, sequences = _event_maps(frame)

    online_rows: list[dict[str, object]] = []
    for row in online_events.itertuples(index=False):
        ordinal = lookup.get((str(row.symbol), str(row.trading_day), row.event_time))
        if ordinal is None:
            continue
        online_rows.append({**row._asdict(), "eligible_ordinal": int(ordinal), "matched": False, "match_id": pd.NA, "event_role": "online"})

    judge_rows: list[dict[str, object]] = []
    excluded = 0
    for row in judge_center_events.itertuples(index=False):
        key = (str(row.symbol), str(row.trading_day), row.event_time)
        center_ordinal = lookup.get(key)
        sequence = sequences.get((str(row.symbol), str(row.trading_day)), [])
        if center_ordinal is None:
            continue
        available = center_ordinal + INDEPENDENT_JUDGE_RADIUS
        if available >= len(sequence):
            excluded += 1
            continue
        judge_rows.append(
            {
                **row._asdict(),
                "judge_center_eligible_ordinal": int(center_ordinal),
                "judge_available_eligible_ordinal": int(available),
                "judge_available_event_time": sequence[available],
                "matched": False,
                "match_id": pd.NA,
                "event_role": "judge",
            }
        )

    online = pd.DataFrame(online_rows)
    judge = pd.DataFrame(judge_rows)
    match_rows: list[dict[str, object]] = []
    match_id = 0
    if not online.empty and not judge.empty:
        for ji, row in judge.iterrows():
            candidates = online.loc[
                (~online["matched"])
                & online["symbol"].astype(str).eq(str(row["symbol"]))
                & online["trading_day"].astype(str).eq(str(row["trading_day"]))
                & online["to_state"].astype(str).eq(str(row["to_state"]))
            ].copy()
            if candidates.empty:
                continue
            candidates["distance"] = (
                candidates["eligible_ordinal"] - int(row["judge_available_eligible_ordinal"])
            ).abs()
            candidates = candidates.loc[candidates["distance"] <= cfg.transition_tolerance_bars]
            if candidates.empty:
                continue
            best = int(candidates.sort_values(["distance", "eligible_ordinal"], kind="stable").index[0])
            match_id += 1
            online.at[best, "matched"] = True
            online.at[best, "match_id"] = match_id
            judge.at[ji, "matched"] = True
            judge.at[ji, "match_id"] = match_id
            delay = int(online.at[best, "eligible_ordinal"] - int(row["judge_available_eligible_ordinal"]))
            match_rows.append(
                {
                    "match_id": match_id,
                    "symbol": str(row["symbol"]),
                    "trading_day": str(row["trading_day"]),
                    "to_state": str(row["to_state"]),
                    "judge_center_time": row["event_time"],
                    "judge_available_time": row["judge_available_event_time"],
                    "online_time": online.at[best, "event_time"],
                    "delay_vs_availability_bars": delay,
                    "delay_vs_availability_minutes": delay * 5,
                }
            )

    tp = int(online["matched"].sum()) if not online.empty else 0
    fp = int((~online["matched"]).sum()) if not online.empty else 0
    fn = int((~judge["matched"]).sum()) if not judge.empty else 0
    precision = tp / (tp + fp) if tp + fp else math.nan
    recall = tp / (tp + fn) if tp + fn else math.nan
    f1 = (
        0.0 if math.isfinite(precision) and math.isfinite(recall) and precision + recall == 0
        else 2.0 * precision * recall / (precision + recall)
        if math.isfinite(precision) and math.isfinite(recall)
        else math.nan
    )
    matches = pd.DataFrame(match_rows)
    eligible_days = max(1, frame.loc[frame["recognition_eligible"].fillna(False), ["symbol", "trading_day"]].drop_duplicates().shape[0])
    summary: dict[str, float | int] = {
        "online_transition_count": int(len(online)),
        "judge_transition_count": int(len(judge)),
        "matched_transition_count": tp,
        "transition_precision": float(precision),
        "transition_recall": float(recall),
        "transition_f1": float(f1),
        "false_transitions_per_day": float(fp / eligible_days),
        "median_delay_vs_availability_bars": float(matches["delay_vs_availability_bars"].median()) if not matches.empty else math.nan,
        "median_delay_vs_availability_minutes": float(matches["delay_vs_availability_minutes"].median()) if not matches.empty else math.nan,
    }
    audit = {
        "judge_center_events_total": int(len(judge_center_events)),
        "judge_events_scored": int(len(judge)),
        "judge_events_excluded_unavailable_same_day": int(excluded),
        "judge_availability_lag_bars": INDEPENDENT_JUDGE_RADIUS,
        "transition_tolerance_bars": int(cfg.transition_tolerance_bars),
    }
    combined = pd.concat([judge, online], ignore_index=True, sort=False)
    return combined, summary, audit


def independent_agreement_grade(asset_results: dict[str, dict[str, object]]) -> dict[str, object]:
    if set(asset_results) != {"000852.SH", "000688.SH"}:
        return {"grade": "inconclusive", "reason": "both frozen assets are required", "failures": []}

    def failures_for(thresholds: dict[str, float]) -> list[str]:
        failures: list[str] = []
        for symbol, result in asset_results.items():
            for metric, threshold in thresholds.items():
                value = float(result.get(metric, math.nan))
                if not math.isfinite(value) or value < threshold:
                    failures.append(f"{symbol}: {metric} < {threshold:.2f}")
        return failures

    strong = failures_for({
        "balanced_accuracy_4state": 0.60,
        "macro_f1_4state": 0.60,
        "transition_f1": 0.45,
        "online_concrete_coverage": 0.85,
    })
    if not strong:
        return {"grade": "strong_independent_algorithmic_agreement", "reason": "all frozen strong gates passed", "failures": []}
    useful = failures_for({
        "balanced_accuracy_4state": 0.50,
        "macro_f1_4state": 0.50,
        "transition_f1": 0.30,
        "online_concrete_coverage": 0.75,
    })
    if not useful:
        return {"grade": "useful_independent_algorithmic_agreement", "reason": "useful gates passed but at least one strong gate failed", "failures": strong}
    return {"grade": "weak_independent_algorithmic_agreement", "reason": "at least one frozen useful gate failed", "failures": useful}


def score_independent_judge(
    state_timeseries: pd.DataFrame,
    *,
    config: RecognitionConfig | None = None,
) -> tuple[
    dict[str, object],
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    dict[str, int],
    pd.DataFrame,
]:
    cfg = config or RecognitionConfig()
    frame, online_events, judge_events = build_independent_judge_frame(state_timeseries, config=cfg)
    point_summary, confusion, per_state = classification_for_columns(
        frame,
        truth_col="independent_judge_available_state",
        prediction_col="online_decoded_state_v3",
        eligible_col="independent_v3_score_eligible",
    )
    yearly = yearly_classification(
        frame,
        truth_col="independent_judge_available_state",
        prediction_col="online_decoded_state_v3",
        eligible_col="independent_v3_score_eligible",
    )
    transition_table, transition_summary, audit = compare_independent_transitions(
        frame,
        online_events,
        judge_events,
        config=cfg,
    )
    return {**point_summary, **transition_summary}, confusion, per_state, yearly, transition_table, audit, frame


__all__ = [
    "INDEPENDENT_JUDGE_RADIUS",
    "INDEPENDENT_JUDGE_WINDOW",
    "INDEPENDENT_REFERENCE_HISTORY",
    "build_independent_judge_frame",
    "classify_independent_geometry",
    "compare_independent_transitions",
    "independent_agreement_grade",
    "score_independent_judge",
]