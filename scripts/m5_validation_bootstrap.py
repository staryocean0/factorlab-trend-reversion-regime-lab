"""Pure M5-4 cluster-bootstrap and Holm helpers.

No files or market data are read here.  The functions implement the M4
pre-registered ISO-week cluster bootstrap for within-direction Strong-Moderate
contrasts and the fixed eight-hypothesis Holm family.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np

BOOTSTRAP_REPLICATES = 5000
BOOTSTRAP_SEED = 20260914
CI_LEVEL = 0.95
HOLM_FAMILY_SIZE = 8


def cluster_bootstrap_difference(records, metric: str, *, alternative: str):
    """Return Strong-Moderate point estimate, percentile CI and one-sided p.

    ``records`` must contain ``week``, ``group`` (MODERATE/STRONG) and the
    requested numeric metric.  Whole ISO weeks are sampled with replacement.
    The same frozen seed is re-initialized for every contrast/metric so results
    are independent of execution order.
    """
    by_week = defaultdict(lambda: {"MODERATE": [0.0, 0], "STRONG": [0.0, 0]})
    values = {"MODERATE": [], "STRONG": []}
    for row in records:
        value = row.get(metric)
        if value is None:
            continue
        value = float(value)
        group = str(row["group"])
        if group not in values or not np.isfinite(value):
            continue
        values[group].append(value)
        cell = by_week[str(row["week"])][group]
        cell[0] += value
        cell[1] += 1
    if not values["MODERATE"] or not values["STRONG"]:
        return None

    point = float(np.mean(values["STRONG"]) - np.mean(values["MODERATE"]))
    weeks = sorted(by_week)
    m_sum = np.array([by_week[w]["MODERATE"][0] for w in weeks], dtype=float)
    m_n = np.array([by_week[w]["MODERATE"][1] for w in weeks], dtype=float)
    s_sum = np.array([by_week[w]["STRONG"][0] for w in weeks], dtype=float)
    s_n = np.array([by_week[w]["STRONG"][1] for w in weeks], dtype=float)
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    draws = rng.integers(0, len(weeks), size=(BOOTSTRAP_REPLICATES, len(weeks)))
    m_count = m_n[draws].sum(axis=1)
    s_count = s_n[draws].sum(axis=1)
    valid = (m_count > 0) & (s_count > 0)
    boot = s_sum[draws].sum(axis=1)[valid] / s_count[valid] - m_sum[draws].sum(axis=1)[valid] / m_count[valid]
    if len(boot) < int(0.9 * BOOTSTRAP_REPLICATES):
        return None
    alpha = 1.0 - CI_LEVEL
    low, high = np.quantile(boot, [alpha / 2.0, 1.0 - alpha / 2.0])
    if alternative == "less":
        p_value = (1.0 + float(np.sum(boot >= 0.0))) / (len(boot) + 1.0)
    elif alternative == "greater":
        p_value = (1.0 + float(np.sum(boot <= 0.0))) / (len(boot) + 1.0)
    else:
        raise ValueError("alternative must be less or greater")
    return {
        "moderate_n": len(values["MODERATE"]),
        "strong_n": len(values["STRONG"]),
        "moderate_mean": float(np.mean(values["MODERATE"])),
        "strong_mean": float(np.mean(values["STRONG"])),
        "strong_minus_moderate": point,
        "ci95": [float(low), float(high)],
        "one_sided_bootstrap_p": float(p_value),
        "valid_bootstrap_replicates": int(len(boot)),
    }


def holm_adjust(p_values):
    """Holm-adjust exactly eight pre-planned p-values."""
    if len(p_values) != HOLM_FAMILY_SIZE:
        raise ValueError("M4 primary family must remain exactly eight")
    p = np.asarray(p_values, dtype=float)
    if np.any(~np.isfinite(p)) or np.any((p < 0.0) | (p > 1.0)):
        raise ValueError("invalid p-value")
    order = np.argsort(p, kind="stable")
    adjusted_sorted = np.empty(len(p), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        candidate = min(1.0, (len(p) - rank) * p[index])
        running = max(running, candidate)
        adjusted_sorted[rank] = running
    adjusted = np.empty(len(p), dtype=float)
    for rank, index in enumerate(order):
        adjusted[index] = adjusted_sorted[rank]
    return [float(value) for value in adjusted]
