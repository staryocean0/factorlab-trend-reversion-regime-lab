"""Pure metric assembly for the one-time M5-4 primary T2=4 Validation."""
from __future__ import annotations

import math
from collections import Counter, defaultdict

import numpy as np

from scripts.m5_validation_bootstrap import cluster_bootstrap_difference

BUCKETS = ("STRONG_DOWN", "DOWN", "SIDEWAYS", "UP", "STRONG_UP")
COMPARED = ("UP", "STRONG_UP", "DOWN", "STRONG_DOWN")
HORIZONS = (1, 3, 5, 10, 20)


def _family(state):
    if state in ("UP", "STRONG_UP"):
        return "UP"
    if state in ("DOWN", "STRONG_DOWN"):
        return "DOWN"
    return "SIDEWAYS"


def _complete(states, index, seq, horizon):
    stop = index + horizon
    return stop < len(states) and all(states[k][0] == seq and states[k][1] is not None for k in range(index, stop + 1))


def _week(timestamp):
    iso = timestamp.isocalendar()
    return f"{int(iso.year):04d}-W{int(iso.week):02d}"


def _episode_records(frame, states, *, validation_start: str, validation_end: str):
    rows = list(frame.itertuples(index=False))
    if len(rows) != len(states):
        raise ValueError("state series must align one-for-one with rows")
    starts = []
    last_state = last_seq = None
    for index, ((seq, state), row) in enumerate(zip(states, rows, strict=True)):
        if state is None:
            last_state = last_seq = None
            continue
        timestamp = row.market_time_shanghai.to_pydatetime()
        is_start = seq != last_seq or state != last_state
        date_label = timestamp.strftime("%Y-%m-%d")
        if is_start and validation_start <= date_label <= validation_end and state in COMPARED:
            direction = _family(state)
            group = "STRONG" if state.startswith("STRONG_") else "MODERATE"
            record = {
                "index": index,
                "state": state,
                "direction": direction,
                "group": group,
                "week": _week(timestamp),
                "timestamp": timestamp.isoformat(),
            }
            sign = 1.0 if direction == "UP" else -1.0
            base_close = float(row.close)
            for horizon in HORIZONS:
                if not _complete(states, index, seq, horizon):
                    record[f"complete_{horizon}"] = False
                    record[f"continuation_{horizon}"] = None
                    record[f"return_{horizon}"] = None
                    continue
                record[f"complete_{horizon}"] = True
                future_state = states[index + horizon][1]
                record[f"continuation_{horizon}"] = float(_family(future_state) == direction)
                future_close = float(rows[index + horizon].close)
                record[f"return_{horizon}"] = sign * math.log(future_close / base_close)
            if _complete(states, index, seq, 5):
                record["survival_5"] = float(all(_family(states[k][1]) == direction for k in range(index + 1, index + 6)))
            else:
                record["survival_5"] = None
            opposite = "DOWN" if direction == "UP" else "UP"
            first_reversal = None
            for k in range(1, 21):
                if not _complete(states, index, seq, k):
                    break
                if _family(states[index + k][1]) == opposite:
                    first_reversal = k
                    break
            for horizon in (5, 10, 20):
                if _complete(states, index, seq, horizon):
                    record[f"reversal_{horizon}"] = float(first_reversal is not None and first_reversal <= horizon)
                    path = []
                    for k in range(1, horizon + 1):
                        close_k = float(rows[index + k].close)
                        path.append(sign * math.log(close_k / base_close))
                    record[f"mfe_{horizon}"] = max(0.0, max(path))
                    record[f"mae_{horizon}"] = max(0.0, -min(path))
                else:
                    record[f"reversal_{horizon}"] = None
                    record[f"mfe_{horizon}"] = None
                    record[f"mae_{horizon}"] = None
            if _complete(states, index, seq, 20):
                record["ttfr_20_event"] = float(first_reversal is not None)
                record["ttfr_20_time_or_censor"] = float(first_reversal if first_reversal is not None else 20)
            else:
                record["ttfr_20_event"] = None
                record["ttfr_20_time_or_censor"] = None
            starts.append(record)
        last_state, last_seq = state, seq
    return starts


def _transition_summaries(frame, states, *, validation_start: str, validation_end: str):
    rows = list(frame.itertuples(index=False))
    one_bar = defaultdict(Counter)
    exits = defaultdict(Counter)
    for i in range(len(states) - 1):
        seq, state = states[i]
        next_seq, next_state = states[i + 1]
        if state is None or next_state is None or seq != next_seq:
            continue
        source_date = rows[i].market_time_shanghai.strftime("%Y-%m-%d")
        dest_date = rows[i + 1].market_time_shanghai.strftime("%Y-%m-%d")
        if validation_start <= source_date <= validation_end and validation_start <= dest_date <= validation_end:
            one_bar[state][next_state] += 1
        if state != next_state and validation_start <= dest_date <= validation_end:
            exits[state][next_state] += 1

    def normalize(matrix):
        output = {}
        for source in BUCKETS:
            counts = matrix[source]
            total = sum(counts.values())
            output[source] = {
                "counts": {dest: int(counts[dest]) for dest in BUCKETS},
                "probabilities": {dest: (float(counts[dest] / total) if total else None) for dest in BUCKETS},
            }
        return output

    return {"one_bar_transition_matrix": normalize(one_bar), "episode_exit_destination_matrix": normalize(exits)}


def _group_summary(records, metric):
    output = {}
    for direction in ("UP", "DOWN"):
        output[direction] = {}
        for group in ("MODERATE", "STRONG"):
            values = [float(r[metric]) for r in records if r["direction"] == direction and r["group"] == group and r.get(metric) is not None]
            output[direction][group] = {"n": len(values), "mean": (float(np.mean(values)) if values else None)}
    return output


def analyze_profile(frame, states, *, validation_start: str, validation_end: str):
    records = _episode_records(frame, states, validation_start=validation_start, validation_end=validation_end)
    result = {
        "episode_counts": {},
        "primary_and_confirmatory": {},
        "descriptive": {},
        **_transition_summaries(frame, states, validation_start=validation_start, validation_end=validation_end),
    }
    for state in COMPARED:
        rows = [r for r in records if r["state"] == state]
        result["episode_counts"][state] = {"total": len(rows), **{f"complete_{h}": sum(bool(r.get(f"complete_{h}")) for r in rows) for h in (5, 10, 20)}}

    for direction in ("UP", "DOWN"):
        subset = [r for r in records if r["direction"] == direction]
        primary = cluster_bootstrap_difference(subset, "survival_5", alternative="less")
        reversal = cluster_bootstrap_difference(subset, "reversal_10", alternative="greater")
        ret5 = cluster_bootstrap_difference(subset, "return_5", alternative="less")
        primary_adequate = bool(primary and primary["moderate_n"] >= 100 and primary["strong_n"] >= 100)
        reversal_adequate = bool(reversal and reversal["moderate_n"] >= 50 and reversal["strong_n"] >= 50)
        return_adequate = bool(ret5 and ret5["moderate_n"] >= 100 and ret5["strong_n"] >= 100)
        result["primary_and_confirmatory"][direction] = {
            "primary_survival_5": primary,
            "secondary_reversal_10": reversal,
            "secondary_return_5": ret5,
            "primary_adequate": primary_adequate,
            "reversal_adequate": reversal_adequate,
            "return_adequate": return_adequate,
        }

    for horizon in HORIZONS:
        result["descriptive"][f"continuation_{horizon}"] = _group_summary(records, f"continuation_{horizon}")
        result["descriptive"][f"return_{horizon}"] = _group_summary(records, f"return_{horizon}")
    for horizon in (5, 10, 20):
        result["descriptive"][f"reversal_{horizon}"] = _group_summary(records, f"reversal_{horizon}")
        result["descriptive"][f"mfe_{horizon}"] = _group_summary(records, f"mfe_{horizon}")
        result["descriptive"][f"mae_{horizon}"] = _group_summary(records, f"mae_{horizon}")
    result["descriptive"]["time_to_first_reversal_20"] = _group_summary(records, "ttfr_20_time_or_censor")
    result["descriptive"]["reversal_event_rate_20"] = _group_summary(records, "ttfr_20_event")
    return result
