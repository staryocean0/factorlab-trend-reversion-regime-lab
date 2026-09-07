"""v0.11: Year × clock × reversal-side stability for the frozen v0.10 lead.

This is a full-surface stability audit, not a rule search. It freezes the v0.5
5m robust-reentry signal, v0.9 1m path resolution, v0.10 symmetric 10bps
barrier and the same eight half-hour blocks. All 2020(partial)-2024 cells are
reported for ALL/LONG/SHORT. 2025 remains unopened.
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

OUT = Path("artifacts/reversal_stability_v0_11")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
YEARS = [2020, 2021, 2022, 2023, 2024]
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
    audits: list[dict] = []
    event_parts: list[pd.DataFrame] = []
    cell_parts: list[pd.DataFrame] = []

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
        year1 = frame1["market_time_shanghai"].dt.year.astype(int)

        audits.append(
            {
                "symbol": symbol,
                "signals_5m": int(signal5.ne(0).sum()),
                "signals_mapped_to_1m": int(signal1.ne(0).sum()),
                "signals_with_clock": int(block1.loc[signal1.ne(0)].notna().sum()),
                "first_signal_day": str(frame1.loc[signal1.ne(0), "trading_day"].min()),
                "last_signal_day": str(frame1.loc[signal1.ne(0), "trading_day"].max()),
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
            sig_values = signal1.loc[valid].to_numpy()
            events = pd.DataFrame(
                {
                    "symbol": symbol,
                    "horizon_minutes": horizon,
                    "market_time_shanghai": frame1.loc[valid, "market_time_shanghai"].astype(str).to_numpy(),
                    "trading_day": frame1.loc[valid, "trading_day"].astype(str).to_numpy(),
                    "year": year1.loc[valid].to_numpy(dtype=int),
                    "clock_block": block1.loc[valid].astype(str).to_numpy(),
                    "signal": sig_values,
                    "side": np.where(sig_values > 0, "LONG", "SHORT"),
                    "outcome": path.loc[valid, "outcome"].astype(str).to_numpy(),
                    "resolution_minutes": path.loc[valid, "resolution_bars"].to_numpy(),
                }
            )
            event_parts.append(events)

            for year in YEARS:
                for clock_name, _, _ in CLOCK_BLOCKS:
                    base = events.loc[
                        events["year"].eq(year) & events["clock_block"].eq(clock_name)
                    ]
                    for side in ["ALL", "LONG", "SHORT"]:
                        subset = base if side == "ALL" else base.loc[base["side"].eq(side)]
                        generic = subset.rename(columns={"resolution_minutes": "resolution_bars"})
                        s = summarize_first_passage(generic).rename(
                            columns={
                                "median_bars_to_target": "median_minutes_to_target",
                                "median_bars_to_stop": "median_minutes_to_stop",
                            }
                        )
                        s.insert(0, "side", side)
                        s.insert(0, "clock_block", clock_name)
                        s.insert(0, "year", year)
                        s.insert(0, "horizon_minutes", horizon)
                        s.insert(0, "symbol", symbol)
                        s["signed_barrier_hit_imbalance_bps"] = BARRIER_BPS * (
                            s["target_first_rate"] - s["stop_first_rate"]
                        )
                        cell_parts.append(s)

    audit = pd.DataFrame(audits)
    events_all = pd.concat(event_parts, ignore_index=True)
    cells = pd.concat(cell_parts, ignore_index=True)

    # Summarize year stability without choosing any clock block.
    stability_rows = []
    for (symbol, horizon, clock_name, side), group in cells.groupby(
        ["symbol", "horizon_minutes", "clock_block", "side"], sort=True
    ):
        nonempty = group.loc[group["events"].gt(0)].copy()
        shares = pd.to_numeric(nonempty["target_share_clean_resolutions"], errors="coerce")
        imbalances = pd.to_numeric(nonempty["signed_barrier_hit_imbalance_bps"], errors="coerce")
        valid_share = shares.notna()
        stability_rows.append(
            {
                "symbol": symbol,
                "horizon_minutes": horizon,
                "clock_block": clock_name,
                "side": side,
                "nonempty_years": int(len(nonempty)),
                "years_with_clean_share": int(valid_share.sum()),
                "positive_years_clean_share": int((shares.loc[valid_share] > 0.5).sum()),
                "negative_years_clean_share": int((shares.loc[valid_share] < 0.5).sum()),
                "median_year_clean_target_share": float(shares.median()) if valid_share.any() else np.nan,
                "min_year_clean_target_share": float(shares.min()) if valid_share.any() else np.nan,
                "max_year_clean_target_share": float(shares.max()) if valid_share.any() else np.nan,
                "median_year_hit_imbalance_bps": float(imbalances.median()) if imbalances.notna().any() else np.nan,
                "total_events": int(nonempty["events"].sum()),
            }
        )
    stability = pd.DataFrame(stability_rows)

    audit.to_csv(OUT / "audit.csv", index=False)
    events_all.to_csv(OUT / "events.csv", index=False)
    cells.to_csv(OUT / "year_clock_side_cells.csv", index=False)
    stability.to_csv(OUT / "stability_summary.csv", index=False)

    # Console view focuses on ALL-side CSI/STAR summaries but prints every clock.
    compact = stability.loc[
        stability["side"].eq("ALL"),
        [
            "symbol",
            "horizon_minutes",
            "clock_block",
            "nonempty_years",
            "positive_years_clean_share",
            "negative_years_clean_share",
            "median_year_clean_target_share",
            "min_year_clean_target_share",
            "max_year_clean_target_share",
            "median_year_hit_imbalance_bps",
            "total_events",
        ],
    ].sort_values(["symbol", "horizon_minutes", "clock_block"])

    print("=== v0.11 STABILITY AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.11 YEAR-STABILITY SUMMARY — ALL SIDES, ALL CLOCK BLOCKS ===")
    print(compact.to_string(index=False))
    print("=== v0.11 CSI1000 10m FULL YEAR x CLOCK x SIDE CLEAN TARGET SHARE ===")
    csi10 = cells.loc[
        cells["symbol"].eq("000852.SH") & cells["horizon_minutes"].eq(10),
        ["year", "clock_block", "side", "events", "target_share_clean_resolutions", "signed_barrier_hit_imbalance_bps"],
    ].sort_values(["clock_block", "year", "side"])
    print(csi10.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
