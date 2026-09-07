"""v0.10: Localize the thin v0.9 10-bps effect by A-share half-hour clock.

This is explicitly a result-driven failure-localization step, not an independent
validation. The v0.5 5m robust-reentry signal, 10-bps symmetric barrier and 1m
post-entry path are frozen. We report all eight continuous-auction half-hour
blocks rather than selecting a winner. 2025 remains unopened.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.first_passage import summarize_first_passage, symmetric_first_passage
from regime_lab.market_data import load_market_data
from regime_lab.reversal_mean_reversion import ReversalFeatureConfig, compute_reversal_features
from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)

OUT = Path("artifacts/reversal_clock_v0_10")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
BARRIER_BPS = 10.0
HORIZONS_MINUTES = [5, 10, 30]

CLOCK_BLOCKS = [
    ("H1_0930_1000", 9 * 60 + 30, 10 * 60),
    ("H2_1000_1030", 10 * 60, 10 * 60 + 30),
    ("H3_1030_1100", 10 * 60 + 30, 11 * 60),
    ("H4_1100_1130", 11 * 60, 11 * 60 + 31),
    ("H5_1300_1330", 13 * 60, 13 * 60 + 30),
    ("H6_1330_1400", 13 * 60 + 30, 14 * 60),
    ("H7_1400_1430", 14 * 60, 14 * 60 + 30),
    ("H8_1430_1500", 14 * 60 + 30, 15 * 60 + 1),
]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


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


def clock_block(times: pd.Series) -> pd.Series:
    minute = times.dt.hour * 60 + times.dt.minute
    out = pd.Series(pd.NA, index=times.index, dtype="string")
    for name, start, end in CLOCK_BLOCKS:
        out.loc[minute.ge(start) & minute.lt(end)] = name
    return out


def main() -> None:
    feature_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(threshold=2.0)
    event_parts = []
    summary_parts = []
    audits = []

    for symbol in SYMBOLS:
        raw5 = load_market_data(symbol, "5m", START, END)
        raw1 = load_market_data(symbol, "1m", START, END)
        frame5 = raw5.loc[
            continuous_auction(raw5) & strict_quality_mask(raw5, expected_source_minutes=5)
        ].copy().reset_index(drop=True)
        frame1 = raw1.loc[
            continuous_auction(raw1) & strict_quality_mask(raw1, expected_source_minutes=1)
        ].copy().reset_index(drop=True)

        features5 = compute_reversal_features(frame5, feature_cfg)
        state5 = compute_robust_residual_state(frame5, features5, robust_cfg)
        signal5 = robust_residual_reentry_signal(frame5, state5, robust_cfg)
        signal_map = pd.Series(signal5.to_numpy(), index=frame5["market_time_shanghai"])
        signal1 = frame1["market_time_shanghai"].map(signal_map).fillna(0).astype("int8")
        block1 = clock_block(frame1["market_time_shanghai"])

        audits.append(
            {
                "symbol": symbol,
                "signals_5m": int(signal5.ne(0).sum()),
                "signals_mapped_to_1m": int(signal1.ne(0).sum()),
                "mapped_clock_blocks": int(block1.loc[signal1.ne(0)].notna().sum()),
            }
        )

        for horizon in HORIZONS_MINUTES:
            path = symmetric_first_passage(
                frame1,
                signal1,
                barrier_bps=BARRIER_BPS,
                horizon_bars=horizon,
            )
            valid = path["valid"].fillna(False).astype(bool)
            events = pd.DataFrame(
                {
                    "symbol": symbol,
                    "horizon_minutes": horizon,
                    "market_time_shanghai": frame1.loc[valid, "market_time_shanghai"].astype(str).to_numpy(),
                    "trading_day": frame1.loc[valid, "trading_day"].astype(str).to_numpy(),
                    "clock_block": block1.loc[valid].astype(str).to_numpy(),
                    "signal": signal1.loc[valid].to_numpy(),
                    "side": np.where(signal1.loc[valid].to_numpy() > 0, "LONG", "SHORT"),
                    "outcome": path.loc[valid, "outcome"].astype(str).to_numpy(),
                    "resolution_minutes": path.loc[valid, "resolution_bars"].to_numpy(),
                }
            )
            event_parts.append(events)

            for name, _, _ in CLOCK_BLOCKS:
                subset = events.loc[events["clock_block"].eq(name)].rename(
                    columns={"resolution_minutes": "resolution_bars"}
                )
                s = summarize_first_passage(subset).rename(
                    columns={
                        "median_bars_to_target": "median_minutes_to_target",
                        "median_bars_to_stop": "median_minutes_to_stop",
                    }
                )
                s.insert(0, "clock_block", name)
                s.insert(0, "horizon_minutes", horizon)
                s.insert(0, "symbol", symbol)
                s["signed_barrier_hit_imbalance_bps"] = BARRIER_BPS * (
                    s["target_first_rate"] - s["stop_first_rate"]
                )
                summary_parts.append(s)

    audit = pd.DataFrame(audits)
    events_all = pd.concat(event_parts, ignore_index=True)
    summary = pd.concat(summary_parts, ignore_index=True)
    audit.to_csv(OUT / "audit.csv", index=False)
    events_all.to_csv(OUT / "events.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    compact = summary[
        [
            "symbol",
            "horizon_minutes",
            "clock_block",
            "events",
            "target_share_clean_resolutions",
            "target_share_ambiguous_as_adverse",
            "signed_barrier_hit_imbalance_bps",
            "median_minutes_to_target",
            "median_minutes_to_stop",
        ]
    ].sort_values(["symbol", "horizon_minutes", "clock_block"])

    print("=== v0.10 CLOCK AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.10 10bps FIRST-PASSAGE BY HALF-HOUR BLOCK ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
