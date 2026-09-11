"""Frozen pure index-price validity primitives.

This module intentionally contains no instrument mapping, cost model, option data,
or horizon selection logic. It reconstructs the original R1/R2 event geometry and
measures signed cash-index price response after the causal event confirmation.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Wave:
    direction: int
    start_idx: int
    end_idx: int
    confirm_idx: int
    start_price: float
    end_price: float

    @property
    def move(self) -> float:
        return self.end_price / self.start_price - 1.0


def detect_waves(prices: np.ndarray, threshold: float) -> list[Wave]:
    p = np.asarray(prices, dtype=float)
    if len(p) < 3 or threshold <= 0.0:
        return []
    waves: list[Wave] = []
    mode = 0
    anchor_idx = 0
    anchor = p[0]
    extreme_idx = 0
    extreme = p[0]
    boot_min_idx = 0
    boot_min = p[0]
    boot_max_idx = 0
    boot_max = p[0]
    for i in range(1, len(p)):
        x = p[i]
        if not np.isfinite(x) or x <= 0.0:
            continue
        if mode == 0:
            if x < boot_min:
                boot_min = x
                boot_min_idx = i
            if x > boot_max:
                boot_max = x
                boot_max_idx = i
            if x / boot_min - 1.0 >= threshold:
                mode = 1
                anchor_idx = boot_min_idx
                anchor = boot_min
                extreme_idx = i
                extreme = x
            elif x / boot_max - 1.0 <= -threshold:
                mode = -1
                anchor_idx = boot_max_idx
                anchor = boot_max
                extreme_idx = i
                extreme = x
            continue
        if mode == 1:
            if x > extreme:
                extreme = x
                extreme_idx = i
            elif x / extreme - 1.0 <= -threshold:
                if extreme_idx > anchor_idx:
                    waves.append(Wave(1, anchor_idx, extreme_idx, i, float(anchor), float(extreme)))
                mode = -1
                anchor_idx = extreme_idx
                anchor = extreme
                extreme_idx = i
                extreme = x
        else:
            if x < extreme:
                extreme = x
                extreme_idx = i
            elif x / extreme - 1.0 >= threshold:
                if extreme_idx > anchor_idx:
                    waves.append(Wave(-1, anchor_idx, extreme_idx, i, float(anchor), float(extreme)))
                mode = 1
                anchor_idx = extreme_idx
                anchor = extreme
                extreme_idx = i
                extreme = x
    return waves


def parent_features(w1: Wave, w2: Wave, prices: np.ndarray) -> dict[str, float]:
    denom = abs(w1.move) + abs(w2.move)
    if denom <= 0.0:
        return {}
    signed = (w2.end_price / w1.start_price - 1.0) / denom
    lo1, hi1 = sorted((w1.start_price, w1.end_price))
    lo2, hi2 = sorted((w2.start_price, w2.end_price))
    inter = max(0.0, min(hi1, hi2) - max(lo1, lo2))
    min_width = min(hi1 - lo1, hi2 - lo2)
    overlap = inter / min_width if min_width > 0.0 else 0.0
    a = max(0, w1.start_idx)
    b = min(len(prices) - 1, w2.end_idx)
    path = prices[a : b + 1]
    path_sum = float(np.nansum(np.abs(np.diff(path)))) if len(path) > 1 else np.nan
    efficiency = abs(w2.end_price - w1.start_price) / path_sum if path_sum > 0.0 else np.nan
    return {
        "signed_drift": float(signed),
        "abs_drift": float(abs(signed)),
        "overlap": float(overlap),
        "parent_eff": float(efficiency),
    }


def last_two_parent(parent_waves: list[Wave], confirm_idxs: list[int], idx: int):
    k = bisect_right(confirm_idxs, idx)
    if k < 2:
        return None
    return parent_waves[k - 2], parent_waves[k - 1]


def structural_boundary(w1: Wave, w2: Wave, parent_sign: int) -> float:
    candidates: list[tuple[int, float]] = []
    for w in (w1, w2):
        if parent_sign > 0:
            candidates.append((w.start_idx, w.start_price) if w.direction > 0 else (w.end_idx, w.end_price))
        else:
            candidates.append((w.start_idx, w.start_price) if w.direction < 0 else (w.end_idx, w.end_price))
    return max(candidates, key=lambda z: z[0])[1]


def first_passage(
    prices: np.ndarray,
    start_idx: int,
    recovery: float,
    failure: float,
    parent_sign: int,
    horizon: int = 1200,
) -> tuple[str, int]:
    end = min(len(prices) - 1, start_idx + horizon)
    for j in range(start_idx, end + 1):
        x = prices[j]
        if parent_sign > 0:
            recovered = x >= recovery
            failed = x <= failure
        else:
            recovered = x <= recovery
            failed = x >= failure
        if recovered and failed:
            return "tie", j
        if recovered:
            return "recovery", j
        if failed:
            return "failure", j
    return "censored", end


def r1_events(
    prices: np.ndarray,
    days: np.ndarray,
    lower_waves: list[Wave],
    parent_waves: list[Wave],
    vol_ref: float,
    cell: str,
) -> pd.DataFrame:
    confirm = [w.confirm_idx for w in parent_waves]
    rows: list[dict] = []
    next_allowed = -1
    for lower in lower_waves:
        if lower.confirm_idx <= next_allowed:
            continue
        pair = last_two_parent(parent_waves, confirm, lower.confirm_idx)
        if not pair:
            continue
        pf = parent_features(*pair, prices)
        if not pf or not np.isfinite(list(pf.values())).all():
            continue
        parent_sign = 1 if pf["signed_drift"] > 0.0 else -1 if pf["signed_drift"] < 0.0 else 0
        if parent_sign == 0 or lower.direction == parent_sign:
            continue
        recovery = lower.start_price
        failure = structural_boundary(*pair, parent_sign)
        current = prices[lower.confirm_idx]
        if parent_sign > 0 and not (failure < current < recovery):
            continue
        if parent_sign < 0 and not (recovery < current < failure):
            continue
        outcome, resolved = first_passage(prices, lower.confirm_idx, recovery, failure, parent_sign)
        if outcome == "tie":
            continue
        rows.append(
            {
                "cell": cell,
                "family": "R1",
                "day": str(days[lower.confirm_idx]),
                "confirm_idx": int(lower.confirm_idx),
                "resolve_idx": int(resolved),
                "signal_dir": int(parent_sign),
                "structural_outcome": outcome,
                "severity": float(abs(lower.move) / vol_ref),
                **pf,
            }
        )
        next_allowed = resolved
    return pd.DataFrame(rows)


def local_vol_features(prices: np.ndarray, idx: int) -> tuple[float, float]:
    returns = np.diff(np.log(prices[max(0, idx - 300) : idx + 1]))
    if len(returns) < 80:
        return np.nan, np.nan
    short = float(np.std(returns[-30:], ddof=0))
    parent = float(np.std(returns[-240:], ddof=0)) if len(returns) >= 240 else float(np.std(returns, ddof=0))
    speed = abs(float(np.log(prices[idx] / prices[max(0, idx - 30)]))) / max(1, min(30, idx))
    return speed, short / parent if parent > 0.0 else np.nan


def r2_events(
    prices: np.ndarray,
    days: np.ndarray,
    parent_waves: list[Wave],
    lower_threshold: float,
    parent_threshold: float,
    cell: str,
) -> pd.DataFrame:
    rows: list[dict] = []
    next_allowed = -1
    wave_cursor = 0
    last2: list[Wave] = []
    for i, x in enumerate(prices):
        while wave_cursor < len(parent_waves) and parent_waves[wave_cursor].confirm_idx <= i:
            last2.append(parent_waves[wave_cursor])
            last2 = last2[-2:]
            wave_cursor += 1
        if i <= next_allowed or len(last2) < 2:
            continue
        pf = parent_features(last2[0], last2[1], prices)
        if not pf or not np.isfinite(list(pf.values())).all():
            continue
        points = [last2[0].start_price, last2[0].end_price, last2[1].start_price, last2[1].end_price]
        low, high = min(points), max(points)
        width = high - low
        if width <= 0.0:
            continue
        if x >= high * (1.0 + lower_threshold):
            breakout_side, edge = 1, high
        elif x <= low * (1.0 - lower_threshold):
            breakout_side, edge = -1, low
        else:
            continue
        continuation = edge * (1.0 + parent_threshold) if breakout_side > 0 else edge * (1.0 - parent_threshold)
        if (breakout_side > 0 and x >= continuation) or (breakout_side < 0 and x <= continuation):
            continue
        end = min(len(prices) - 1, i + 1200)
        outcome = "censored"
        resolved = end
        for j in range(i, end + 1):
            z = prices[j]
            if breakout_side > 0:
                if z <= edge:
                    outcome, resolved = "reentry", j
                    break
                if z >= continuation:
                    outcome, resolved = "continuation", j
                    break
            else:
                if z >= edge:
                    outcome, resolved = "reentry", j
                    break
                if z <= continuation:
                    outcome, resolved = "continuation", j
                    break
        speed, vol_ratio = local_vol_features(prices, i)
        rows.append(
            {
                "cell": cell,
                "family": "R2",
                "day": str(days[i]),
                "confirm_idx": int(i),
                "resolve_idx": int(resolved),
                "signal_dir": int(-breakout_side),
                "breakout_side": int(breakout_side),
                "structural_outcome": outcome,
                "outside_ratio": float(abs(x - edge) / edge / (width / edge)),
                "break_speed": float(speed / lower_threshold) if lower_threshold > 0.0 else np.nan,
                "local_vol_ratio": float(vol_ratio),
                **pf,
            }
        )
        next_allowed = resolved
    return pd.DataFrame(rows)


def generate_events(
    prices: np.ndarray,
    days: np.ndarray,
    thresholds: dict[str, float],
    vol_ref: float,
) -> pd.DataFrame:
    waves = {name: detect_waves(prices, float(thresholds[name])) for name in ("S1", "S2", "S3")}
    parts = [
        r1_events(prices, days, waves["S1"], waves["S2"], vol_ref, "R1_A"),
        r1_events(prices, days, waves["S2"], waves["S3"], vol_ref, "R1_B"),
        r2_events(prices, days, waves["S2"], float(thresholds["S1"]), float(thresholds["S2"]), "R2_A"),
        r2_events(prices, days, waves["S3"], float(thresholds["S2"]), float(thresholds["S3"]), "R2_B"),
    ]
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()


def evaluate_events(
    events: pd.DataFrame,
    prices: np.ndarray,
    days: np.ndarray,
    horizons: Iterable[int],
    symbol: str,
) -> pd.DataFrame:
    rows: list[dict] = []
    n = len(prices)
    for event in events.itertuples(index=False):
        entry_idx = int(event.confirm_idx) + 1
        if entry_idx >= n:
            continue
        entry_price = float(prices[entry_idx])
        direction = int(event.signal_dir)
        if not np.isfinite(entry_price) or entry_price <= 0.0 or direction not in {-1, 1}:
            continue
        for h in horizons:
            exit_idx = entry_idx + int(h)
            if exit_idx >= n:
                continue
            exit_price = float(prices[exit_idx])
            raw = exit_price / entry_price - 1.0
            signed = direction * raw
            path = prices[entry_idx + 1 : exit_idx + 1] / entry_price - 1.0
            signed_path = direction * path
            rows.append(
                {
                    "symbol": symbol,
                    "cell": event.cell,
                    "family": event.family,
                    "event_day": str(event.day),
                    "entry_day": str(days[entry_idx]),
                    "entry_idx": entry_idx,
                    "signal_dir": direction,
                    "side": "LONG" if direction > 0 else "SHORT",
                    "horizon": int(h),
                    "signed_return": float(signed),
                    "MFE": float(np.max(signed_path)) if len(signed_path) else 0.0,
                    "MAE": float(np.min(signed_path)) if len(signed_path) else 0.0,
                    "structural_outcome": event.structural_outcome,
                }
            )
    return pd.DataFrame(rows)


def _stats(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"n": 0, "mean": None, "median": None, "win_rate": None, "mean_MFE": None, "mean_MAE": None}
    x = frame["signed_return"].to_numpy(float)
    return {
        "n": int(len(frame)),
        "mean": float(np.mean(x)),
        "median": float(np.median(x)),
        "win_rate": float(np.mean(x > 0.0)),
        "mean_MFE": float(frame["MFE"].mean()),
        "mean_MAE": float(frame["MAE"].mean()),
    }


def summarize_window(frame: pd.DataFrame, annual_years: list[str]) -> dict:
    out: dict[str, dict] = {}
    for cell in ("R1_A", "R1_B", "R2_A", "R2_B"):
        c = frame.loc[frame["cell"].eq(cell)]
        cell_out: dict[str, dict] = {}
        for h in (1, 5, 15, 30, 60, 120, 240):
            block = c.loc[c["horizon"].eq(h)]
            pooled = _stats(block)
            annual = {}
            positive_years = 0
            for year in annual_years:
                y = block.loc[block["entry_day"].str.startswith(year)]
                ys = _stats(y)
                annual[year] = ys
                if ys["mean"] is not None and ys["mean"] > 0.0:
                    positive_years += 1
            by_side = {side: _stats(block.loc[block["side"].eq(side)]) for side in ("LONG", "SHORT")}
            side_sufficient = by_side["LONG"]["n"] >= 30 and by_side["SHORT"]["n"] >= 30
            both_side_positive = (
                bool(by_side["LONG"]["mean"] > 0.0 and by_side["SHORT"]["mean"] > 0.0) if side_sufficient else None
            )
            flags = {
                "pooled_mean_positive": bool(pooled["mean"] is not None and pooled["mean"] > 0.0),
                "pooled_median_positive": bool(pooled["median"] is not None and pooled["median"] > 0.0),
                "win_rate_above_50pct": bool(pooled["win_rate"] is not None and pooled["win_rate"] > 0.5),
                "positive_annual_mean_min_4_of_5": bool(len(annual_years) == 5 and positive_years >= 4),
                "both_LONG_and_SHORT_mean_positive_when_each_side_n_ge_30": both_side_positive,
            }
            robust = all(value is True for value in flags.values())
            cell_out[str(h)] = {
                "pooled": pooled,
                "annual": annual,
                "positive_annual_mean_years": int(positive_years),
                "by_side": by_side,
                "support_flags": flags,
                "robust_price_edge": bool(robust),
            }
        out[cell] = cell_out
    return out
