"""v0.8: Can the transient MR excursion be monetized before adverse continuation?

This experiment freezes the v0.5 robust-residual re-entry signal. It does not
search for a new entry rule. After next-bar-open entry it measures symmetric
5/10 bps target-vs-stop first passage within 30/60 trading minutes. If both
barriers are touched in the same 5m OHLC bar, ordering is explicitly ambiguous.
2025 remains unopened.
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

OUT = Path("artifacts/reversal_first_passage_v0_8")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
BARRIER_BPS = [5.0, 10.0]
HORIZONS_MINUTES = [30, 60]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def _truthy(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    return series.astype(str).str.strip().str.lower().isin({"true", "1", "yes"})


def strict_quality_mask(frame: pd.DataFrame) -> pd.Series:
    mask = pd.Series(True, index=frame.index)
    if "high_frequency_analysis_eligible" in frame.columns:
        mask &= _truthy(frame["high_frequency_analysis_eligible"])
    if "causal_flat_fill" in frame.columns:
        mask &= ~_truthy(frame["causal_flat_fill"])
    if "source_minute_count" in frame.columns:
        source_count = pd.to_numeric(frame["source_minute_count"], errors="coerce")
        mask &= source_count.ge(5)
    return mask


def main() -> None:
    feature_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(threshold=2.0)
    event_parts = []
    summary_parts = []
    audits = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        mask = continuous_auction(raw) & strict_quality_mask(raw)
        frame = raw.loc[mask].copy().reset_index(drop=True)

        features = compute_reversal_features(frame, feature_cfg)
        state = compute_robust_residual_state(frame, features, robust_cfg)
        signal = robust_residual_reentry_signal(frame, state, robust_cfg)
        prior_extreme_z = pd.to_numeric(state["residual_robust_z"], errors="coerce").shift(1)

        audits.append(
            {
                "symbol": symbol,
                "raw_rows": len(raw),
                "research_rows": len(frame),
                "days": frame["trading_day"].nunique(),
                "signal_bars": int(signal.ne(0).sum()),
                "signal_days": int(frame.loc[signal.ne(0), "trading_day"].nunique()),
                "long_signals": int(signal.gt(0).sum()),
                "short_signals": int(signal.lt(0).sum()),
            }
        )

        for barrier in BARRIER_BPS:
            for horizon in HORIZONS_MINUTES:
                path = symmetric_first_passage(
                    frame,
                    signal,
                    barrier_bps=barrier,
                    horizon_bars=horizon // robust_cfg.bar_minutes,
                )
                valid = path["valid"].fillna(False).astype(bool)
                events = pd.DataFrame(
                    {
                        "symbol": symbol,
                        "barrier_bps": barrier,
                        "horizon_minutes": horizon,
                        "market_time_shanghai": frame.loc[valid, "market_time_shanghai"].astype(str).to_numpy(),
                        "trading_day": frame.loc[valid, "trading_day"].astype(str).to_numpy(),
                        "signal": signal.loc[valid].to_numpy(),
                        "side": np.where(signal.loc[valid].to_numpy() > 0, "LONG", "SHORT"),
                        "prior_extreme_z": prior_extreme_z.loc[valid].to_numpy(),
                        "entry_price": path.loc[valid, "entry_price"].to_numpy(),
                        "outcome": path.loc[valid, "outcome"].astype(str).to_numpy(),
                        "resolution_bars": path.loc[valid, "resolution_bars"].to_numpy(),
                    }
                )
                event_parts.append(events)

                for side in ["ALL", "LONG", "SHORT"]:
                    subset = events if side == "ALL" else events.loc[events["side"].eq(side)]
                    s = summarize_first_passage(subset)
                    s.insert(0, "side", side)
                    s.insert(0, "horizon_minutes", horizon)
                    s.insert(0, "barrier_bps", barrier)
                    s.insert(0, "symbol", symbol)
                    summary_parts.append(s)

    audit = pd.DataFrame(audits)
    events_all = pd.concat(event_parts, ignore_index=True)
    summary = pd.concat(summary_parts, ignore_index=True)

    audit.to_csv(OUT / "audit.csv", index=False)
    events_all.to_csv(OUT / "events.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    compact = summary.loc[
        summary["side"].eq("ALL"),
        [
            "symbol",
            "barrier_bps",
            "horizon_minutes",
            "events",
            "target_first_rate",
            "stop_first_rate",
            "ambiguous_rate",
            "neither_rate",
            "target_share_clean_resolutions",
            "target_share_ambiguous_as_adverse",
            "median_bars_to_target",
            "median_bars_to_stop",
        ],
    ].sort_values(["symbol", "barrier_bps", "horizon_minutes"])

    print("=== v0.8 FIRST-PASSAGE AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.8 ROBUST MR TARGET-vs-STOP FIRST PASSAGE ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
