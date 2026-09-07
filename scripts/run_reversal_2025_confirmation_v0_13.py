"""v0.13 preregistered 2025 historical confirmation.

IMPORTANT: the frozen contract lives in docs/research/V0_13_2025_CONFIRMATION_PROTOCOL.md
and was committed before this workflow is executed against 2025.

Candidate: CSI1000, negative overnight gap, H1 09:30-10:00, LONG robust
residual re-entry threshold 2.0, next-1m-open entry, symmetric 10bps barriers,
10m primary cap (5m/30m frozen robustness). Same-1m-bar target+stop is scored
as stop; timeout exits at cap close.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.barrier_policy import (
    evaluate_barrier_timeout_policy,
    summarize_barrier_timeout,
)
from regime_lab.market_data import load_market_data
from regime_lab.reversal_mean_reversion import ReversalFeatureConfig, compute_reversal_features
from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)

OUT = Path("artifacts/reversal_2025_confirmation_v0_13")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOL = "000852.SH"
START = "2020-07-23"
END = "2025-12-31"
BARRIER_BPS = 10.0
HORIZONS = [5, 10, 30]
PRIMARY_HORIZON = 10


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def h1_mask(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.ge(9 * 60 + 30) & minute.lt(10 * 60)


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def strict_quality_mask(frame: pd.DataFrame, *, expected_source_minutes: int) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    if "high_frequency_analysis_eligible" in frame.columns:
        mask &= _truthy(frame["high_frequency_analysis_eligible"])
    if "causal_flat_fill" in frame.columns:
        mask &= ~_truthy(frame["causal_flat_fill"])
    if "source_minute_count" in frame.columns:
        count = pd.to_numeric(frame["source_minute_count"], errors="coerce")
        mask &= count.ge(expected_source_minutes)
    return mask


def daily_gap_map(frame5: pd.DataFrame) -> pd.DataFrame:
    daily = (
        frame5.groupby("trading_day", sort=True)
        .agg(day_open=("open", "first"), day_close=("close", "last"))
        .reset_index()
    )
    daily["prev_close"] = pd.to_numeric(daily["day_close"], errors="coerce").shift(1)
    day_open = pd.to_numeric(daily["day_open"], errors="coerce")
    daily["overnight_gap_log"] = np.log(day_open / daily["prev_close"])
    return daily[["trading_day", "overnight_gap_log"]]


def role_for_day(day: pd.Series) -> pd.Series:
    year = pd.to_numeric(day.astype(str).str[:4], errors="coerce")
    return pd.Series(
        np.where(year.eq(2025), "2025_CONFIRMATION", "2020_2024_DEVELOPMENT"),
        index=day.index,
        dtype="string",
    )


def entry_alignment_audit(
    frame5: pd.DataFrame,
    candidate5: pd.Series,
    frame1: pd.DataFrame,
) -> pd.DataFrame:
    next1_map = pd.Series(
        pd.to_numeric(frame1["open"], errors="coerce").shift(-1).to_numpy(),
        index=frame1["market_time_shanghai"],
    )
    next5 = pd.to_numeric(frame5["open"], errors="coerce").shift(-1)
    same_day5 = frame5["trading_day"].shift(-1).eq(frame5["trading_day"])
    rows = []
    for role, role_mask in {
        "2020_2024_DEVELOPMENT": frame5["market_time_shanghai"].dt.year.le(2024),
        "2025_CONFIRMATION": frame5["market_time_shanghai"].dt.year.eq(2025),
    }.items():
        mask = candidate5 & same_day5 & role_mask
        times = frame5.loc[mask, "market_time_shanghai"]
        e5 = next5.loc[mask].to_numpy(dtype=float)
        e1 = times.map(next1_map).to_numpy(dtype=float)
        finite = np.isfinite(e5) & np.isfinite(e1)
        diffs = np.abs(e5[finite] - e1[finite])
        rows.append(
            {
                "role": role,
                "candidate_5m_signals": int(mask.sum()),
                "audited_entries": int(finite.sum()),
                "entry_exact_match_rate": float(np.mean(diffs == 0.0)) if len(diffs) else np.nan,
                "entry_max_abs_point_diff": float(np.max(diffs)) if len(diffs) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    raw5 = load_market_data(SYMBOL, "5m", START, END)
    raw1 = load_market_data(SYMBOL, "1m", START, END)
    frame5 = raw5.loc[
        continuous_auction(raw5) & strict_quality_mask(raw5, expected_source_minutes=5)
    ].copy().reset_index(drop=True)
    frame1 = raw1.loc[
        continuous_auction(raw1) & strict_quality_mask(raw1, expected_source_minutes=1)
    ].copy().reset_index(drop=True)

    feature_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(threshold=2.0)
    features5 = compute_reversal_features(frame5, feature_cfg)
    state5 = compute_robust_residual_state(frame5, features5, robust_cfg)
    signal5 = robust_residual_reentry_signal(frame5, state5, robust_cfg)

    gaps = daily_gap_map(frame5).set_index("trading_day")["overnight_gap_log"]
    gap5 = frame5["trading_day"].astype(str).map(gaps)
    candidate5 = signal5.eq(1) & h1_mask(frame5) & gap5.lt(0)

    signal_map = pd.Series(signal5.to_numpy(), index=frame5["market_time_shanghai"])
    signal1 = frame1["market_time_shanghai"].map(signal_map).fillna(0).astype("int8")
    gap1 = frame1["trading_day"].astype(str).map(gaps)
    candidate1 = signal1.eq(1) & h1_mask(frame1) & gap1.lt(0)
    frozen_signal1 = signal1.where(candidate1, 0)
    role1 = role_for_day(frame1["trading_day"])

    audit = entry_alignment_audit(frame5, candidate5, frame1)
    audit["candidate_1m_mapped_development"] = int(
        (candidate1 & role1.eq("2020_2024_DEVELOPMENT")).sum()
    )
    audit["candidate_1m_mapped_confirmation"] = int(
        (candidate1 & role1.eq("2025_CONFIRMATION")).sum()
    )

    event_parts = []
    summary_parts = []
    for horizon in HORIZONS:
        policy = evaluate_barrier_timeout_policy(
            frame1,
            frozen_signal1,
            barrier_bps=BARRIER_BPS,
            horizon_bars=horizon,
        )
        valid = policy["valid"].fillna(False).astype(bool)
        events = pd.DataFrame(
            {
                "role": role1.loc[valid].astype(str).to_numpy(),
                "horizon_minutes": horizon,
                "market_time_shanghai": frame1.loc[valid, "market_time_shanghai"].astype(str).to_numpy(),
                "trading_day": frame1.loc[valid, "trading_day"].astype(str).to_numpy(),
                "overnight_gap_bps": (gap1.loc[valid].to_numpy() * 1e4),
                "entry_price": policy.loc[valid, "entry_price"].to_numpy(),
                "outcome": policy.loc[valid, "outcome"].astype(str).to_numpy(),
                "resolution_minutes": policy.loc[valid, "resolution_bars"].to_numpy(),
                "gross_policy_bps": policy.loc[valid, "gross_policy_bps"].to_numpy(),
            }
        )
        event_parts.append(events)

        for role in ["2020_2024_DEVELOPMENT", "2025_CONFIRMATION"]:
            subset = events.loc[events["role"].eq(role)].rename(
                columns={"resolution_minutes": "resolution_bars"}
            )
            s = summarize_barrier_timeout(subset)
            s.insert(0, "horizon_minutes", horizon)
            s.insert(0, "role", role)
            s["trading_days"] = int(
                events.loc[events["role"].eq(role), "trading_day"].nunique()
            )
            s["is_primary_horizon"] = horizon == PRIMARY_HORIZON
            summary_parts.append(s)

    events_all = pd.concat(event_parts, ignore_index=True)
    summary = pd.concat(summary_parts, ignore_index=True)

    audit.to_csv(OUT / "entry_audit.csv", index=False)
    events_all.to_csv(OUT / "events.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    primary = summary.loc[
        summary["role"].eq("2025_CONFIRMATION")
        & summary["horizon_minutes"].eq(PRIMARY_HORIZON)
    ].iloc[0]
    n = int(primary["events"])
    criteria = {
        "event_count_at_least_20": n >= 20,
        "clean_target_share_gt_50pct": bool(primary["clean_target_share"] > 0.5) if n else False,
        "conservative_target_share_gt_50pct": bool(primary["conservative_target_share"] > 0.5) if n else False,
        "gross_policy_mean_gt_0bps": bool(primary["gross_policy_mean_bps"] > 0.0) if n else False,
    }
    if n < 20:
        verdict = "INCONCLUSIVE_LOW_COUNT"
    elif all(criteria.values()):
        verdict = "DIRECTIONALLY_SUPPORTIVE_HISTORICAL_CONFIRMATION"
    else:
        verdict = "NOT_SUPPORTED_ON_FROZEN_2025_PRIMARY"

    decision = pd.DataFrame(
        [
            {
                "primary_horizon_minutes": PRIMARY_HORIZON,
                "verdict": verdict,
                **criteria,
            }
        ]
    )
    decision.to_csv(OUT / "decision.csv", index=False)

    print("=== v0.13 ENTRY ALIGNMENT AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.13 FROZEN POLICY — DEVELOPMENT VS 2025 CONFIRMATION ===")
    print(summary.to_string(index=False))
    print("=== v0.13 PREDECLARED PRIMARY DECISION ===")
    print(decision.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
