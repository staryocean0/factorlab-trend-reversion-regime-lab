"""Split-safe transition summaries for the frozen M5-4 Validation."""
from __future__ import annotations

from collections import Counter, defaultdict

BUCKETS = ("STRONG_DOWN", "DOWN", "SIDEWAYS", "UP", "STRONG_UP")


def transition_summaries(frame, states, *, validation_start: str, validation_end: str):
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
        start_date = rows[start].market_time_shanghai.strftime("%Y-%m-%d")
        if validation_start <= start_date <= validation_end and j < len(states) and states[j][0] == seq and states[j][1] is not None:
            exit_date = rows[j].market_time_shanghai.strftime("%Y-%m-%d")
            if validation_start <= exit_date <= validation_end:
                exits[state][states[j][1]] += 1
        i = j

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

    return {
        "one_bar_transition_matrix": normalize(one_bar),
        "episode_exit_destination_matrix": normalize(exits),
    }
