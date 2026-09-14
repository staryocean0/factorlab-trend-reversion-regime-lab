"""Pure helpers for M5-2 Development sample-adequacy checks."""
from __future__ import annotations

import math
from collections import Counter, deque

from factor_lab.market_state.trend_regime_baseline import TrendRegimeBaselineConfig, _log_close_ols


def five_bucket(score: float, t1: float, t2: float) -> str:
    if score < -t2:
        return "STRONG_DOWN"
    if score < -t1:
        return "DOWN"
    if score <= t1:
        return "SIDEWAYS"
    if score <= t2:
        return "UP"
    return "STRONG_UP"


def is_contiguous(previous, current, close_times: tuple[str, ...]) -> bool:
    positions = {label: i for i, label in enumerate(close_times)}
    a, b = previous.strftime("%H:%M"), current.strftime("%H:%M")
    if a not in positions or b not in positions:
        return False
    if previous.date() == current.date():
        return positions[b] == positions[a] + 1
    return positions[a] == len(close_times) - 1 and positions[b] == 0


def build_state_series(frame, *, close_times: tuple[str, ...], t1: float, t2: float):
    config = TrendRegimeBaselineConfig()
    window = deque(maxlen=20)
    sequence_id, previous = 0, None
    states, bad = [], Counter()
    valid_grid = set(close_times)
    for row in frame.itertuples(index=False):
        timestamp = row.market_time_shanghai.to_pydatetime()
        ok = timestamp.strftime("%H:%M") in valid_grid
        if hasattr(row, "high_frequency_analysis_eligible") and not bool(row.high_frequency_analysis_eligible):
            ok = False
            bad["ineligible_rows"] += 1
        try:
            close = float(row.close)
        except (TypeError, ValueError):
            close = float("nan")
        if not math.isfinite(close) or close <= 0:
            ok = False
            bad["invalid_close_rows"] += 1
        if previous is not None and not is_contiguous(previous, timestamp, close_times):
            ok = False
            bad["cadence_breaks"] += 1
        if not ok:
            sequence_id += 1
            window.clear()
            previous = None
            states.append((sequence_id, None))
            continue
        window.append(close)
        previous = timestamp
        state = None
        if len(window) == 20:
            _, slope_t, _ = _log_close_ols(tuple(window), config=config)
            state = five_bucket(slope_t, t1, t2)
        states.append((sequence_id, state))
    return states, dict(bad)


def episode_adequacy(states):
    compared = ("UP", "STRONG_UP", "DOWN", "STRONG_DOWN")
    starts, last_state, last_seq = [], None, None
    for index, (seq, state) in enumerate(states):
        if state is None:
            last_state = last_seq = None
            continue
        if seq != last_seq or state != last_state:
            if state in compared:
                starts.append((index, seq, state))
        last_state, last_seq = state, seq
    counts = {name: Counter(total=0, complete_5=0, complete_10=0, complete_20=0) for name in compared}
    for index, seq, state in starts:
        counts[state]["total"] += 1
        for horizon in (5, 10, 20):
            stop = index + horizon
            if stop < len(states) and all(states[k][0] == seq and states[k][1] is not None for k in range(index, stop + 1)):
                counts[state][f"complete_{horizon}"] += 1
    result = {name: dict(value) for name, value in counts.items()}
    readiness = {}
    for direction, moderate, strong in (("UP", "UP", "STRONG_UP"), ("DOWN", "DOWN", "STRONG_DOWN")):
        m, s = result[moderate], result[strong]
        readiness[direction] = {
            "moderate_complete_5": m["complete_5"],
            "strong_complete_5": s["complete_5"],
            "moderate_complete_10": m["complete_10"],
            "strong_complete_10": s["complete_10"],
            "moderate_complete_20": m["complete_20"],
            "strong_complete_20": s["complete_20"],
            "development_primary_count_floor_met": m["complete_5"] >= 100 and s["complete_5"] >= 100,
            "development_secondary_count_floor_met": min(m["complete_10"], s["complete_10"], m["complete_20"], s["complete_20"]) >= 50,
        }
    return {"episode_counts": result, "directional_sample_adequacy": readiness}
