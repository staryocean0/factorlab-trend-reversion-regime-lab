"""v0.12: Does the stable CSI1000 H1 aggregate lead reflect overnight-gap fading?

Only the 09:30-10:00 block is examined because the overnight gap is a natural
prior-only coordinate there. The v0.5 5m robust-reentry signal, v0.9 1m path,
10bps symmetric barriers and 5/10/30m caps remain frozen. No gap threshold is
optimized: events are classified only by whether the reversal trade points
against (GAP_FADE) or with (GAP_FOLLOW) the signed previous-close to day-open
gap. 2025 remains unopened.
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

OUT = Path("artifacts/reversal_overnight_gap_v0_12")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
YEARS = [2020, 2021, 2022, 2023, 2024]
BARRIER_BPS = 10.0
HORIZONS_MINUTES = [5, 10, 30]
H1_START = 9 * 60 + 30
H1_END = 10 * 60


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def h1_mask(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.ge(H1_START) & minute.lt(H1_END)


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
    """Return causal day open and previous available continuous-auction close."""
    daily = (
        frame5.groupby("trading_day", sort=True)
        .agg(day_open=("open", "first"), day_close=("close", "last"))
        .reset_index()
    )
    daily["prev_close"] = pd.to_numeric(daily["day_close"], errors="coerce").shift(1)
    day_open = pd.to_numeric(daily["day_open"], errors="coerce")
    daily["overnight_gap_log"] = np.log(day_open / daily["prev_close"])
    return daily[["trading_day", "day_open", "prev_close", "overnight_gap_log"]]


def gap_relation(signal: pd.Series, gap: pd.Series) -> pd.Series:
    prod = pd.to_numeric(signal, errors="coerce") * pd.to_numeric(gap, errors="coerce")
    out = pd.Series("UNDEFINED_OR_ZERO", index=signal.index, dtype="string")
    out.loc[prod.lt(0)] = "GAP_FADE"
    out.loc[prod.gt(0)] = "GAP_FOLLOW"
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

        gaps = daily_gap_map(frame5).set_index("trading_day")
        gap1 = frame1["trading_day"].astype(str).map(gaps["overnight_gap_log"])
        relation1 = gap_relation(signal1, gap1)
        year1 = frame1["market_time_shanghai"].dt.year.astype(int)
        h1 = h1_mask(frame1)

        audits.append(
            {
                "symbol": symbol,
                "h1_signals": int((signal1.ne(0) & h1).sum()),
                "h1_gap_fade": int((signal1.ne(0) & h1 & relation1.eq("GAP_FADE")).sum()),
                "h1_gap_follow": int((signal1.ne(0) & h1 & relation1.eq("GAP_FOLLOW")).sum()),
                "h1_gap_undefined_or_zero": int((signal1.ne(0) & h1 & relation1.eq("UNDEFINED_OR_ZERO")).sum()),
                "median_abs_gap_bps_h1_signals": float(
                    (gap1.loc[signal1.ne(0) & h1].abs() * 1e4).median()
                ),
            }
        )

        for horizon in HORIZONS_MINUTES:
            path = symmetric_first_passage(
                frame1,
                signal1.where(h1, 0),
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
                    "signal": sig_values,
                    "side": np.where(sig_values > 0, "LONG", "SHORT"),
                    "overnight_gap_log": gap1.loc[valid].to_numpy(),
                    "overnight_gap_bps": (gap1.loc[valid].to_numpy() * 1e4),
                    "gap_relation": relation1.loc[valid].astype(str).to_numpy(),
                    "outcome": path.loc[valid, "outcome"].astype(str).to_numpy(),
                    "resolution_minutes": path.loc[valid, "resolution_bars"].to_numpy(),
                }
            )
            event_parts.append(events)

            for year in YEARS:
                for relation in ["ALL", "GAP_FADE", "GAP_FOLLOW"]:
                    base = events.loc[events["year"].eq(year)]
                    if relation != "ALL":
                        base = base.loc[base["gap_relation"].eq(relation)]
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
                        s.insert(0, "gap_relation", relation)
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

    stability_rows = []
    for (symbol, horizon, relation, side), group in cells.groupby(
        ["symbol", "horizon_minutes", "gap_relation", "side"], sort=True
    ):
        nonempty = group.loc[group["events"].gt(0)].copy()
        shares = pd.to_numeric(nonempty["target_share_clean_resolutions"], errors="coerce")
        valid_share = shares.notna()
        stability_rows.append(
            {
                "symbol": symbol,
                "horizon_minutes": horizon,
                "gap_relation": relation,
                "side": side,
                "nonempty_years": int(len(nonempty)),
                "positive_years_clean_share": int((shares.loc[valid_share] > 0.5).sum()),
                "negative_years_clean_share": int((shares.loc[valid_share] < 0.5).sum()),
                "median_year_clean_target_share": float(shares.median()) if valid_share.any() else np.nan,
                "min_year_clean_target_share": float(shares.min()) if valid_share.any() else np.nan,
                "max_year_clean_target_share": float(shares.max()) if valid_share.any() else np.nan,
                "total_events": int(nonempty["events"].sum()),
            }
        )
    stability = pd.DataFrame(stability_rows)

    audit.to_csv(OUT / "audit.csv", index=False)
    events_all.to_csv(OUT / "events.csv", index=False)
    cells.to_csv(OUT / "year_gap_side_cells.csv", index=False)
    stability.to_csv(OUT / "stability_summary.csv", index=False)

    compact = stability.loc[
        stability["symbol"].eq("000852.SH"),
        [
            "horizon_minutes",
            "gap_relation",
            "side",
            "nonempty_years",
            "positive_years_clean_share",
            "negative_years_clean_share",
            "median_year_clean_target_share",
            "min_year_clean_target_share",
            "max_year_clean_target_share",
            "total_events",
        ],
    ].sort_values(["horizon_minutes", "gap_relation", "side"])

    print("=== v0.12 H1 OVERNIGHT-GAP AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.12 CSI1000 YEAR-STABILITY BY GAP RELATION AND SIDE ===")
    print(compact.to_string(index=False))
    print("=== v0.12 CSI1000 10m YEAR CELLS ===")
    csi10 = cells.loc[
        cells["symbol"].eq("000852.SH") & cells["horizon_minutes"].eq(10),
        ["year", "gap_relation", "side", "events", "target_share_clean_resolutions", "signed_barrier_hit_imbalance_bps"],
    ].sort_values(["gap_relation", "year", "side"])
    print(csi10.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
