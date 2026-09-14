"""Duration summaries required by the frozen M4 descriptive protocol."""
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


def duration_summaries(frame, states, *, validation_start: str, validation_end: str):
    rows = list(frame.itertuples(index=False))
    exact = defaultdict(list)
    family = defaultdict(list)
    i = 0
    while i < len(states):
        seq, state = states[i]
        if state is None:
            i += 1
            continue
        start = i
        j = i + 1
        while j < len(states) and states[j][0] == seq and states[j][1] == state:
            j += 1
        date_label = rows[start].market_time_shanghai.strftime("%Y-%m-%d")
        if validation_start <= date_label <= validation_end:
            exact[state].append(j - start)
        i = j

    i = 0
    while i < len(states):
        seq, state = states[i]
        if state is None:
            i += 1
            continue
        fam = _family(state)
        start = i
        j = i + 1
        while j < len(states) and states[j][0] == seq and states[j][1] is not None and _family(states[j][1]) == fam:
            j += 1
        date_label = rows[start].market_time_shanghai.strftime("%Y-%m-%d")
        if validation_start <= date_label <= validation_end:
            family[fam].append(j - start)
        i = j

    def summarize(values):
        return {"n": len(values), "mean_bars": (float(np.mean(values)) if values else None), "median_bars": (float(np.median(values)) if values else None)}

    return {
        "exact_bucket_episode_duration": {state: summarize(exact[state]) for state in BUCKETS},
        "directional_family_episode_duration": {name: summarize(family[name]) for name in ("DOWN", "SIDEWAYS", "UP")},
    }
