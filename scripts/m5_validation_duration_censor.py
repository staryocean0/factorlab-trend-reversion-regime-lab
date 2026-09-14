from __future__ import annotations

from collections import defaultdict
import numpy as np

BUCKETS = ("STRONG_DOWN", "DOWN", "SIDEWAYS", "UP", "STRONG_UP")


def _family(state):
    if state in ("UP", "STRONG_UP"):
        return "UP"
    if state in ("DOWN", "STRONG_DOWN"):
        return "DOWN"
    return "SIDEWAYS"


def _summarize(cell):
    values = cell["complete"]
    return {
        "complete_n": len(values),
        "right_censored_n": int(cell["censored"]),
        "mean_bars_complete": float(np.mean(values)) if values else None,
        "median_bars_complete": float(np.median(values)) if values else None,
    }


def duration_summaries(frame, states, *, validation_start, validation_end):
    rows = list(frame.itertuples(index=False))
    exact = defaultdict(lambda: {"complete": [], "censored": 0})
    family = defaultdict(lambda: {"complete": [], "censored": 0})
    for mode, store in (("exact", exact), ("family", family)):
        i = 0
        while i < len(states):
            seq, state = states[i]
            if state is None:
                i += 1
                continue
            key = state if mode == "exact" else _family(state)
            start = i
            j = i + 1
            while j < len(states) and states[j][0] == seq and states[j][1] is not None and ((states[j][1] == state) if mode == "exact" else (_family(states[j][1]) == key)):
                j += 1
            date_label = rows[start].market_time_shanghai.strftime("%Y-%m-%d")
            if validation_start <= date_label <= validation_end:
                if j == len(states):
                    store[key]["censored"] += 1
                else:
                    store[key]["complete"].append(j - start)
            i = j
    return {
        "exact_bucket_episode_duration": {state: _summarize(exact[state]) for state in BUCKETS},
        "directional_family_episode_duration": {name: _summarize(family[name]) for name in ("DOWN", "SIDEWAYS", "UP")},
    }
