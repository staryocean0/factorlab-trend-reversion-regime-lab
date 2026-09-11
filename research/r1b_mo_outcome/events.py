"""Certified R1_B S2-inside-S3 engine plus the inherited temporal-completion clocks.

Wave detection and certified-event membership are a byte-level port of the archived
`run_rmr_stage1_common_probe.detect_waves` / `r1_events` functions. Thresholds are
taken from the pre-execution freeze; nothing is refit.
"""
from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd

S2_THRESHOLD = 0.006891654009228464
S3_THRESHOLD = 0.013783308018456928
HORIZON_BARS = 1200
VOL_REF = 0.013783308018456928
JOINABLE_START = date(2022, 7, 22)
JOINABLE_END = date(2025, 12, 31)


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


@dataclass(frozen=True)
class UnderlyingEvent:
    confirm_idx: int
    entry_idx: int
    exit_idx: int | None
    horizon_end_idx: int
    parent_sign: int
    recovery: float
    failure: float
    entry_price: float
    exit_price: float | None
    confirm_day: str
    entry_day: str
    exit_day: str | None
    horizon_day: str | None
    confirm_ts: pd.Timestamp
    entry_ts: pd.Timestamp
    exit_ts: pd.Timestamp | None
    horizon_ts: pd.Timestamp | None
    structural_outcome: str
    exit_class: str | None
    missingness: str | None
    holding_bars: int | None


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


def last_two_parent(parent_waves: list[Wave], confirm_idxs: list[int], idx: int) -> tuple[Wave, Wave] | None:
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


def first_passage(prices, start_idx, recovery, failure, parent_sign, horizon=HORIZON_BARS):
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


def _entry_in_interval(price: float, recovery: float, failure: float, parent_sign: int) -> bool:
    if parent_sign > 0:
        return failure < price < recovery
    return recovery < price < failure


def _crossed_failure(price: float, failure: float, parent_sign: int) -> bool:
    if parent_sign > 0:
        return price <= failure
    return price >= failure


def first_parent_aligned_s2_confirm(s2_waves: list[Wave], parent_sign: int, after_idx: int) -> int | None:
    confirms = [w.confirm_idx for w in s2_waves if w.direction == parent_sign and w.confirm_idx > after_idx]
    if not confirms:
        return None
    return min(confirms)


def temporal_exit(
    prices: np.ndarray,
    entry_idx: int,
    horizon_end_idx: int,
    parent_sign: int,
    failure: float,
    completion_idx: int | None,
) -> tuple[str, int]:
    last = len(prices) - 1
    if horizon_end_idx > last:
        scan_end = last
        truncated = True
    else:
        scan_end = horizon_end_idx
        truncated = False
    for j in range(entry_idx, scan_end + 1):
        if _crossed_failure(float(prices[j]), failure, parent_sign):
            return "parent_failure", j
        if completion_idx is not None and j == completion_idx:
            return "temporal_completion", j
    if truncated:
        return "underlying_horizon_truncated", scan_end
    return "censored", scan_end


def certified_r1b_rows(prices: np.ndarray, s2_waves: list[Wave], s3_waves: list[Wave]) -> list[dict]:
    confirm = [w.confirm_idx for w in s3_waves]
    rows: list[dict] = []
    next_allowed = -1
    for lower in s2_waves:
        if lower.confirm_idx <= next_allowed:
            continue
        pair = last_two_parent(s3_waves, confirm, lower.confirm_idx)
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
                "confirm_idx": int(lower.confirm_idx),
                "parent_sign": int(parent_sign),
                "recovery": float(recovery),
                "failure": float(failure),
                "structural_outcome": str(outcome),
                "structural_resolve_idx": int(resolved),
                "severity": float(abs(lower.move) / VOL_REF),
                **pf,
            }
        )
        next_allowed = resolved
    return rows


def build_underlying_events(
    frame: pd.DataFrame,
    *,
    joinable_start: date = JOINABLE_START,
    joinable_end: date = JOINABLE_END,
    s2_threshold: float = S2_THRESHOLD,
    s3_threshold: float = S3_THRESHOLD,
    horizon_bars: int = HORIZON_BARS,
) -> list[UnderlyingEvent]:
    prices = pd.to_numeric(frame["close"], errors="coerce").to_numpy(float)
    days = frame["trading_day"].astype(str).to_numpy()
    stamps = pd.to_datetime(frame["market_time_shanghai"])
    s2_waves = detect_waves(prices, s2_threshold)
    s3_waves = detect_waves(prices, s3_threshold)
    certified = certified_r1b_rows(prices, s2_waves, s3_waves)
    events: list[UnderlyingEvent] = []
    last = len(prices) - 1
    for row in certified:
        confirm_idx = int(row["confirm_idx"])
        confirm_day = date.fromisoformat(str(days[confirm_idx]))
        if confirm_day > joinable_end:
            continue
        if confirm_idx >= last:
            if joinable_start <= confirm_day <= joinable_end:
                events.append(
                    _incomplete(
                        confirm_idx,
                        None,
                        row,
                        stamps,
                        days,
                        missingness="entry_invalid",
                    )
                )
            continue
        entry_idx = confirm_idx + 1
        entry_day = date.fromisoformat(str(days[entry_idx]))
        if entry_day < joinable_start or entry_day > joinable_end:
            continue
        entry_price = float(prices[entry_idx])
        if not _entry_in_interval(entry_price, float(row["recovery"]), float(row["failure"]), int(row["parent_sign"])):
            events.append(
                _incomplete(
                    confirm_idx,
                    entry_idx,
                    row,
                    stamps,
                    days,
                    missingness="entry_invalid",
                    entry_price=entry_price,
                )
            )
            continue
        horizon_end = entry_idx + horizon_bars
        horizon_day = str(days[horizon_end]) if horizon_end <= last else None
        horizon_ts = stamps[horizon_end] if horizon_end <= last else None
        completion_idx = first_parent_aligned_s2_confirm(s2_waves, int(row["parent_sign"]), confirm_idx)
        exit_class, exit_idx = temporal_exit(
            prices,
            entry_idx,
            horizon_end,
            int(row["parent_sign"]),
            float(row["failure"]),
            completion_idx,
        )
        if exit_class == "underlying_horizon_truncated":
            events.append(
                UnderlyingEvent(
                    confirm_idx=confirm_idx,
                    entry_idx=entry_idx,
                    exit_idx=None,
                    horizon_end_idx=horizon_end,
                    parent_sign=int(row["parent_sign"]),
                    recovery=float(row["recovery"]),
                    failure=float(row["failure"]),
                    entry_price=entry_price,
                    exit_price=None,
                    confirm_day=str(days[confirm_idx]),
                    entry_day=str(days[entry_idx]),
                    exit_day=None,
                    horizon_day=horizon_day,
                    confirm_ts=stamps[confirm_idx],
                    entry_ts=stamps[entry_idx],
                    exit_ts=None,
                    horizon_ts=horizon_ts,
                    structural_outcome=str(row["structural_outcome"]),
                    exit_class=None,
                    missingness="underlying_horizon_truncated",
                    holding_bars=None,
                )
            )
            continue
        events.append(
            UnderlyingEvent(
                confirm_idx=confirm_idx,
                entry_idx=entry_idx,
                exit_idx=int(exit_idx),
                horizon_end_idx=horizon_end,
                parent_sign=int(row["parent_sign"]),
                recovery=float(row["recovery"]),
                failure=float(row["failure"]),
                entry_price=entry_price,
                exit_price=float(prices[exit_idx]),
                confirm_day=str(days[confirm_idx]),
                entry_day=str(days[entry_idx]),
                exit_day=str(days[exit_idx]),
                horizon_day=horizon_day,
                confirm_ts=stamps[confirm_idx],
                entry_ts=stamps[entry_idx],
                exit_ts=stamps[exit_idx],
                horizon_ts=horizon_ts,
                structural_outcome=str(row["structural_outcome"]),
                exit_class=exit_class,
                missingness=None,
                holding_bars=int(exit_idx - entry_idx),
            )
        )
    return events


def _incomplete(
    confirm_idx: int,
    entry_idx: int | None,
    row: dict,
    stamps,
    days,
    *,
    missingness: str,
    entry_price: float | None = None,
) -> UnderlyingEvent:
    return UnderlyingEvent(
        confirm_idx=confirm_idx,
        entry_idx=-1 if entry_idx is None else entry_idx,
        exit_idx=None,
        horizon_end_idx=-1 if entry_idx is None else entry_idx + HORIZON_BARS,
        parent_sign=int(row["parent_sign"]),
        recovery=float(row["recovery"]),
        failure=float(row["failure"]),
        entry_price=float("nan") if entry_price is None else entry_price,
        exit_price=None,
        confirm_day=str(days[confirm_idx]),
        entry_day="" if entry_idx is None else str(days[entry_idx]),
        exit_day=None,
        horizon_day=None,
        confirm_ts=stamps[confirm_idx],
        entry_ts=stamps[confirm_idx] if entry_idx is None else stamps[entry_idx],
        exit_ts=None,
        horizon_ts=None,
        structural_outcome=str(row["structural_outcome"]),
        exit_class=None,
        missingness=missingness,
        holding_bars=None,
    )
