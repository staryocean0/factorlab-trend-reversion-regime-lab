from __future__ import annotations

from bisect import bisect_right
import hashlib
from typing import Iterable

import numpy as np
import pandas as pd

from research.index_price_validity.core import Wave, detect_waves, generate_events, parent_features

FEATURES = ("parent_abs_drift", "parent_efficiency", "log1p_parent_age_bars", "local_vol_30_over_240")
SEGMENTS = ((0, 1), (1, 5), (5, 15), (15, 30), (30, 60), (60, 120), (120, 240))
HORIZONS = (1, 5, 15, 30, 60, 120, 240)


def rolling_vol_ratio(prices: np.ndarray) -> np.ndarray:
    p = np.asarray(prices, dtype=float)
    ret = np.full(len(p), np.nan, dtype=float)
    if len(p) > 1:
        ret[1:] = np.diff(np.log(p))
    s = pd.Series(ret)
    short = s.rolling(30, min_periods=30).std(ddof=0).to_numpy(float)
    long = s.rolling(240, min_periods=240).std(ddof=0).to_numpy(float)
    out = np.full(len(p), np.nan, dtype=float)
    good = np.isfinite(short) & np.isfinite(long) & (long > 0)
    out[good] = short[good] / long[good]
    return out


def _clock_bucket(ts) -> int:
    return int((int(ts.hour) * 60 + int(ts.minute)) // 30)


def _parent_state(
    info_idx: int,
    parent_waves: list[Wave],
    confirm_idxs: list[int],
    prices: np.ndarray,
    cache: dict[int, dict | None],
) -> dict | None:
    k = bisect_right(confirm_idxs, info_idx)
    if k < 2:
        return None
    if k not in cache:
        pair = parent_waves[k - 2], parent_waves[k - 1]
        pf = parent_features(*pair, prices)
        if not pf or not np.isfinite(list(pf.values())).all():
            cache[k] = None
        else:
            sign = 1 if pf["signed_drift"] > 0 else -1 if pf["signed_drift"] < 0 else 0
            cache[k] = {
                "parent_direction": int(sign),
                "parent_abs_drift": float(pf["abs_drift"]),
                "parent_efficiency": float(pf["parent_eff"]),
                "last_parent_confirm_idx": int(parent_waves[k - 1].confirm_idx),
            }
    state = cache[k]
    if state is None or state["parent_direction"] == 0:
        return None
    out = dict(state)
    out["parent_age_bars"] = int(info_idx - state["last_parent_confirm_idx"])
    out["log1p_parent_age_bars"] = float(np.log1p(max(0, out["parent_age_bars"])))
    return out


def build_r1_events_and_controls(
    prices: np.ndarray,
    days: np.ndarray,
    times: pd.Series,
    thresholds: dict[str, float],
    vol_ref: float,
    start_day: str,
    end_day: str,
    max_horizon: int = 240,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    prices = np.asarray(prices, dtype=float)
    days = np.asarray(days, dtype=str)
    waves = {name: detect_waves(prices, float(thresholds[name])) for name in ("S1", "S2", "S3")}
    events_all = generate_events(prices, days, thresholds, vol_ref)
    events_all = events_all.loc[events_all["cell"].isin(["R1_A", "R1_B"])].copy()
    events_all["entry_idx"] = events_all["confirm_idx"].astype(int) + 1
    events_all = events_all.loc[events_all["entry_idx"] + max_horizon < len(prices)].copy()
    event_entry_by_cell = {
        cell: sorted(events_all.loc[events_all["cell"].eq(cell), "entry_idx"].astype(int).tolist())
        for cell in ("R1_A", "R1_B")
    }
    event_entry_sets = {cell: set(v) for cell, v in event_entry_by_cell.items()}
    vol_ratio = rolling_vol_ratio(prices)

    event_rows: list[dict] = []
    control_rows: list[dict] = []
    parent_scale = {"R1_A": "S2", "R1_B": "S3"}
    for cell in ("R1_A", "R1_B"):
        parent_waves = waves[parent_scale[cell]]
        confirms = [int(w.confirm_idx) for w in parent_waves]
        cache: dict[int, dict | None] = {}

        ev = events_all.loc[events_all["cell"].eq(cell)].copy()
        for row in ev.itertuples(index=False):
            entry_idx = int(row.entry_idx)
            entry_day = str(days[entry_idx])
            if entry_day < start_day or entry_day > end_day:
                continue
            info_idx = entry_idx - 1
            state = _parent_state(info_idx, parent_waves, confirms, prices, cache)
            if state is None or state["parent_direction"] != int(row.signal_dir):
                continue
            vr = float(vol_ratio[info_idx])
            if not np.isfinite(vr):
                continue
            event_rows.append(
                {
                    "cell": cell,
                    "event_day": entry_day,
                    "entry_idx": entry_idx,
                    "parent_direction": int(row.signal_dir),
                    "side": "LONG" if int(row.signal_dir) > 0 else "SHORT",
                    "clock_bucket": _clock_bucket(times.iloc[entry_idx]),
                    "calendar_year": entry_day[:4],
                    "severity": float(row.severity),
                    "parent_abs_drift": state["parent_abs_drift"],
                    "parent_efficiency": state["parent_efficiency"],
                    "parent_age_bars": state["parent_age_bars"],
                    "log1p_parent_age_bars": state["log1p_parent_age_bars"],
                    "local_vol_30_over_240": vr,
                }
            )

        event_entries = event_entry_by_cell[cell]
        event_set = event_entry_sets[cell]
        valid_idx = np.flatnonzero((days >= start_day) & (days <= end_day))
        if len(valid_idx) == 0:
            continue
        lo = max(1, int(valid_idx[0]))
        hi = min(int(valid_idx[-1]), len(prices) - max_horizon - 1)
        for entry_idx in range(lo, hi + 1):
            if entry_idx in event_set:
                continue
            pos = bisect_right(event_entries, entry_idx) - 1
            if pos >= 0 and 0 <= entry_idx - event_entries[pos] <= max_horizon:
                continue
            info_idx = entry_idx - 1
            state = _parent_state(info_idx, parent_waves, confirms, prices, cache)
            if state is None:
                continue
            vr = float(vol_ratio[info_idx])
            if not np.isfinite(vr):
                continue
            day = str(days[entry_idx])
            control_rows.append(
                {
                    "cell": cell,
                    "control_day": day,
                    "entry_idx": int(entry_idx),
                    "parent_direction": int(state["parent_direction"]),
                    "clock_bucket": _clock_bucket(times.iloc[entry_idx]),
                    "calendar_year": day[:4],
                    "parent_abs_drift": state["parent_abs_drift"],
                    "parent_efficiency": state["parent_efficiency"],
                    "parent_age_bars": state["parent_age_bars"],
                    "log1p_parent_age_bars": state["log1p_parent_age_bars"],
                    "local_vol_30_over_240": vr,
                }
            )
    return pd.DataFrame(event_rows), pd.DataFrame(control_rows)


def _robust_center_scale(frame: pd.DataFrame) -> tuple[dict[str, float], dict[str, float]]:
    centers: dict[str, float] = {}
    scales: dict[str, float] = {}
    for feature in FEATURES:
        x = frame[feature].to_numpy(float)
        center = float(np.median(x))
        mad = float(np.median(np.abs(x - center))) * 1.4826
        scale = mad
        if not np.isfinite(scale) or scale <= 0:
            scale = float(np.std(x, ddof=0))
        if not np.isfinite(scale) or scale <= 0:
            scale = 1.0
        centers[feature] = center
        scales[feature] = scale
    return centers, scales


def match_events(events: pd.DataFrame, controls: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    if events.empty or controls.empty:
        return pd.DataFrame(), {"eligible_events": int(len(events)), "matched_events": 0, "coverage": 0.0}
    controls = controls.sort_values("entry_idx", kind="stable").reset_index(drop=True).copy()
    events = events.sort_values("entry_idx", kind="stable").reset_index(drop=True).copy()
    norms: dict[str, tuple[dict[str, float], dict[str, float]]] = {}
    for year, block in controls.groupby("calendar_year", sort=True):
        norms[str(year)] = _robust_center_scale(block)
    for feature in FEATURES:
        controls[f"z_{feature}"] = np.nan
    for year, (centers, scales) in norms.items():
        mask = controls["calendar_year"].eq(year)
        for feature in FEATURES:
            controls.loc[mask, f"z_{feature}"] = (controls.loc[mask, feature] - centers[feature]) / scales[feature]
    group_positions = {
        (str(y), int(d), int(b)): np.asarray(list(idx), dtype=int)
        for (y, d, b), idx in controls.groupby(["calendar_year", "parent_direction", "clock_bucket"], sort=False).groups.items()
    }
    rows: list[dict] = []
    for event in events.itertuples(index=False):
        year = str(event.calendar_year)
        key = (year, int(event.parent_direction), int(event.clock_bucket))
        positions = group_positions.get(key)
        if positions is None or len(positions) == 0 or year not in norms:
            continue
        centers, scales = norms[year]
        ez = np.array([(float(getattr(event, f)) - centers[f]) / scales[f] for f in FEATURES], dtype=float)
        cz = controls.loc[positions, [f"z_{f}" for f in FEATURES]].to_numpy(float)
        d2 = np.sum((cz - ez) ** 2, axis=1)
        pick_local = int(np.argmin(d2))
        pick_pos = int(positions[pick_local])
        control = controls.iloc[pick_pos]
        rows.append(
            {
                "cell": event.cell,
                "event_day": event.event_day,
                "event_entry_idx": int(event.entry_idx),
                "control_day": str(control.control_day),
                "control_entry_idx": int(control.entry_idx),
                "side": event.side,
                "parent_direction": int(event.parent_direction),
                "clock_bucket": int(event.clock_bucket),
                "calendar_year": year,
                "severity": float(event.severity),
                "match_distance": float(np.sqrt(d2[pick_local])),
                **{f"event_{f}": float(getattr(event, f)) for f in FEATURES},
                **{f"control_{f}": float(control[f]) for f in FEATURES},
            }
        )
    matched = pd.DataFrame(rows)
    meta = {
        "eligible_events": int(len(events)),
        "matched_events": int(len(matched)),
        "coverage": float(len(matched) / len(events)) if len(events) else 0.0,
        "unique_controls": int(matched["control_entry_idx"].nunique()) if not matched.empty else 0,
        "median_match_distance": float(matched["match_distance"].median()) if not matched.empty else None,
        "p90_match_distance": float(matched["match_distance"].quantile(0.90)) if not matched.empty else None,
    }
    return matched, meta


def paired_outcomes(
    matches: pd.DataFrame,
    prices: np.ndarray,
    horizons: Iterable[int] = HORIZONS,
) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(prices)
    for pair in matches.itertuples(index=False):
        direction = int(pair.parent_direction)
        e0 = int(pair.event_entry_idx)
        c0 = int(pair.control_entry_idx)
        for h in horizons:
            h = int(h)
            if e0 + h >= n or c0 + h >= n:
                continue
            er = direction * (float(prices[e0 + h]) / float(prices[e0]) - 1.0)
            cr = direction * (float(prices[c0 + h]) / float(prices[c0]) - 1.0)
            rows.append(
                {
                    "cell": pair.cell,
                    "event_day": pair.event_day,
                    "control_day": pair.control_day,
                    "event_entry_idx": e0,
                    "control_entry_idx": c0,
                    "side": pair.side,
                    "parent_direction": direction,
                    "horizon": h,
                    "event_signed_return": float(er),
                    "control_signed_return": float(cr),
                    "incremental_return": float(er - cr),
                    "match_distance": float(pair.match_distance),
                }
            )
    return pd.DataFrame(rows)


def _signed_log_bp(prices: np.ndarray, a: int, b: int, direction: int) -> float:
    return float(direction * np.log(float(prices[b]) / float(prices[a])) * 10000.0)


def _day_bounds(days: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n = len(days)
    first = np.empty(n, dtype=int)
    last = np.empty(n, dtype=int)
    start = 0
    while start < n:
        day = days[start]
        end = start
        while end + 1 < n and days[end + 1] == day:
            end += 1
        first[start : end + 1] = start
        last[start : end + 1] = end
        start = end + 1
    return first, last


def _session_components(prices: np.ndarray, days: np.ndarray, entry_idx: int, exit_idx: int, direction: int, day_last: np.ndarray) -> tuple[float, float, float]:
    last = int(day_last[entry_idx])
    if last >= exit_idx:
        return _signed_log_bp(prices, entry_idx, exit_idx, direction), 0.0, 0.0
    next_open = last + 1
    return (
        _signed_log_bp(prices, entry_idx, last, direction),
        _signed_log_bp(prices, last, next_open, direction),
        _signed_log_bp(prices, next_open, exit_idx, direction),
    )


def _extrema_timing(prices: np.ndarray, entry_idx: int, horizon: int, direction: int) -> tuple[int, int]:
    base = float(prices[entry_idx])
    path = direction * (prices[entry_idx + 1 : entry_idx + horizon + 1] / base - 1.0)
    return int(np.argmax(path) + 1), int(np.argmin(path) + 1)


def path_attribution(matches: pd.DataFrame, prices: np.ndarray, days: np.ndarray) -> pd.DataFrame:
    rows: list[dict] = []
    _, day_last = _day_bounds(days)
    for pair in matches.itertuples(index=False):
        direction = int(pair.parent_direction)
        e0 = int(pair.event_entry_idx)
        c0 = int(pair.control_entry_idx)
        if e0 + 240 >= len(prices) or c0 + 240 >= len(prices):
            continue
        row = {
            "cell": pair.cell,
            "event_day": pair.event_day,
            "control_day": pair.control_day,
            "side": pair.side,
            "parent_direction": direction,
            "event_entry_idx": e0,
            "control_entry_idx": c0,
            "match_distance": float(pair.match_distance),
        }
        for a, b in SEGMENTS:
            ev = _signed_log_bp(prices, e0 + a, e0 + b, direction)
            cv = _signed_log_bp(prices, c0 + a, c0 + b, direction)
            key = f"seg_{a}_{b}"
            row[f"event_{key}_bp"] = ev
            row[f"control_{key}_bp"] = cv
            row[f"incremental_{key}_bp"] = ev - cv
        es = _session_components(prices, days, e0, e0 + 240, direction, day_last)
        cs = _session_components(prices, days, c0, c0 + 240, direction, day_last)
        for name, ev, cv in zip(("same_session", "overnight", "next_session"), es, cs):
            row[f"event_{name}_bp"] = ev
            row[f"control_{name}_bp"] = cv
            row[f"incremental_{name}_bp"] = ev - cv
        e_mfe, e_mae = _extrema_timing(prices, e0, 240, direction)
        c_mfe, c_mae = _extrema_timing(prices, c0, 240, direction)
        row.update(
            {
                "event_bars_to_MFE": e_mfe,
                "event_bars_to_MAE": e_mae,
                "control_bars_to_MFE": c_mfe,
                "control_bars_to_MAE": c_mae,
            }
        )
        rows.append(row)
    return pd.DataFrame(rows)


def _basic(values: pd.Series) -> dict:
    if len(values) == 0:
        return {"n": 0, "mean": None, "median": None, "positive_fraction": None}
    x = values.to_numpy(float)
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "positive_fraction": float(np.mean(x > 0)),
    }


def cluster_bootstrap_mean_ci(frame: pd.DataFrame, value_col: str, day_col: str, reps: int, seed: int, key: str) -> tuple[float | None, float | None]:
    if frame.empty:
        return None, None
    daily = frame.groupby(day_col, sort=True)[value_col].agg(["sum", "count"])
    if len(daily) < 2:
        mean = float(frame[value_col].mean())
        return mean, mean
    digest = int(hashlib.sha256(key.encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng((int(seed) + digest) % (2**32 - 1))
    sums = daily["sum"].to_numpy(float)
    counts = daily["count"].to_numpy(float)
    n_days = len(daily)
    draws = np.empty(int(reps), dtype=float)
    for i in range(int(reps)):
        idx = rng.integers(0, n_days, size=n_days)
        draws[i] = float(sums[idx].sum() / counts[idx].sum())
    return float(np.quantile(draws, 0.025)), float(np.quantile(draws, 0.975))


def summarize_incremental(
    outcomes: pd.DataFrame,
    match_meta: dict[str, dict],
    years: Iterable[str] = ("2021", "2022", "2023", "2024", "2025"),
    reps: int = 2000,
    seed: int = 20260911,
) -> dict:
    result: dict[str, dict] = {}
    for cell in ("R1_A", "R1_B"):
        c = outcomes.loc[outcomes["cell"].eq(cell)]
        cell_out: dict[str, dict] = {}
        meta = match_meta[cell]
        for h in HORIZONS:
            block = c.loc[c["horizon"].eq(h)]
            event = _basic(block["event_signed_return"])
            control = _basic(block["control_signed_return"])
            inc = _basic(block["incremental_return"])
            low, high = cluster_bootstrap_mean_ci(block, "incremental_return", "event_day", reps, seed, f"{cell}-{h}")
            annual = {}
            positive_years = 0
            for year in years:
                y = block.loc[block["event_day"].str.startswith(str(year)), "incremental_return"]
                stats = _basic(y)
                annual[str(year)] = stats
                if stats["mean"] is not None and stats["mean"] > 0:
                    positive_years += 1
            by_side = {}
            both_side_positive = True
            for side in ("LONG", "SHORT"):
                s = block.loc[block["side"].eq(side), "incremental_return"]
                stats = _basic(s)
                by_side[side] = stats
                if stats["n"] < 30 or stats["mean"] is None or stats["mean"] <= 0:
                    both_side_positive = False
            flags = {
                "match_coverage_min_80pct": bool(meta["coverage"] >= 0.80),
                "pooled_incremental_mean_gt_0": bool(inc["mean"] is not None and inc["mean"] > 0),
                "bootstrap_95pct_lower_gt_0": bool(low is not None and low > 0),
                "positive_annual_incremental_mean_min_4_of_5": bool(positive_years >= 4),
                "both_LONG_and_SHORT_incremental_mean_gt_0_when_each_side_n_ge_30": bool(both_side_positive),
            }
            cell_out[str(h)] = {
                "matching": meta,
                "event": event,
                "control": control,
                "incremental": inc,
                "bootstrap_95pct_mean_ci": [low, high],
                "annual_incremental": annual,
                "positive_annual_incremental_mean_years": int(positive_years),
                "incremental_by_side": by_side,
                "support_flags": flags,
                "strong_incremental_support": bool(all(flags.values())),
            }
        result[cell] = cell_out
    return result


def summarize_path(path: pd.DataFrame) -> dict:
    result: dict[str, dict] = {}
    for cell in ("R1_A", "R1_B"):
        block = path.loc[path["cell"].eq(cell)]
        segments = {}
        for a, b in SEGMENTS:
            key = f"seg_{a}_{b}"
            segments[key] = {
                "event_mean_bp": float(block[f"event_{key}_bp"].mean()) if len(block) else None,
                "control_mean_bp": float(block[f"control_{key}_bp"].mean()) if len(block) else None,
                "incremental_mean_bp": float(block[f"incremental_{key}_bp"].mean()) if len(block) else None,
            }
        session = {}
        for name in ("same_session", "overnight", "next_session"):
            session[name] = {
                "event_mean_bp": float(block[f"event_{name}_bp"].mean()) if len(block) else None,
                "control_mean_bp": float(block[f"control_{name}_bp"].mean()) if len(block) else None,
                "incremental_mean_bp": float(block[f"incremental_{name}_bp"].mean()) if len(block) else None,
            }
        extrema = {
            "event_median_bars_to_MFE": float(block["event_bars_to_MFE"].median()) if len(block) else None,
            "event_median_bars_to_MAE": float(block["event_bars_to_MAE"].median()) if len(block) else None,
            "control_median_bars_to_MFE": float(block["control_bars_to_MFE"].median()) if len(block) else None,
            "control_median_bars_to_MAE": float(block["control_bars_to_MAE"].median()) if len(block) else None,
            "event_fraction_MFE_by_30": float((block["event_bars_to_MFE"] <= 30).mean()) if len(block) else None,
            "event_fraction_MFE_by_60": float((block["event_bars_to_MFE"] <= 60).mean()) if len(block) else None,
            "event_fraction_MFE_by_120": float((block["event_bars_to_MFE"] <= 120).mean()) if len(block) else None,
        }
        result[cell] = {"n": int(len(block)), "segments": segments, "h240_session_decomposition": session, "extrema_timing": extrema}
    return result
