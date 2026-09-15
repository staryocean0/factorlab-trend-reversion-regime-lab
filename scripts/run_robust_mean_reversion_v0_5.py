"""Test a robust residual distribution for mean-reversion state.

This iteration does not use a trend filter. It keeps the causal 120m prior-close
EMA anchor, but replaces ATR-based displacement with a robust z-score of the
anchor residual relative to the previous 240 trading minutes. Signal occurs
only on re-entry from |z| >= 2 back inside the band. 2025 remains unopened.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.market_data import load_market_data
from regime_lab.reversal_mean_reversion import (
    ReversalFeatureConfig,
    compute_reversal_features,
    diagnostic_event_return,
)
from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)

OUT = Path("artifacts/robust_mean_reversion_v0_5")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
HORIZONS_MINUTES = [5, 10, 15, 30, 60, 120]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    years = sorted(events["year"].unique())
    for (symbol, horizon), base in events.groupby(["symbol", "horizon_minutes"]):
        for year in ["ALL", *years]:
            g = base if year == "ALL" else base.loc[base["year"] == year]
            for side in ["ALL", "LONG", "SHORT"]:
                x = g
                if side == "LONG":
                    x = g.loc[g["signal"] > 0]
                elif side == "SHORT":
                    x = g.loc[g["signal"] < 0]
                r = x["event_return"].dropna()
                rows.append(
                    {
                        "strategy": "MR_ROBUST_REENTRY",
                        "symbol": symbol,
                        "horizon_minutes": horizon,
                        "year": year,
                        "side": side,
                        "events": int(len(x)),
                        "valid_events": int(len(r)),
                        "mean_return_bps": float(r.mean() * 1e4) if len(r) else np.nan,
                        "median_return_bps": float(r.median() * 1e4) if len(r) else np.nan,
                        "win_rate": float((r > 0).mean()) if len(r) else np.nan,
                        "p05_return_bps": float(r.quantile(0.05) * 1e4) if len(r) else np.nan,
                        "p95_return_bps": float(r.quantile(0.95) * 1e4) if len(r) else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    base_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(
        bar_minutes=5,
        distribution_minutes=240,
        threshold=2.0,
    )
    event_parts = []
    counts = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        frame = raw.loc[continuous_auction(raw)].copy().reset_index(drop=True)
        base = compute_reversal_features(frame, base_cfg)
        state = compute_robust_residual_state(frame, base, robust_cfg)
        signal = robust_residual_reentry_signal(frame, state, robust_cfg)
        mask = signal.ne(0)

        counts.append(
            {
                "strategy": "MR_ROBUST_REENTRY",
                "symbol": symbol,
                "signal_bars": int(mask.sum()),
                "signal_days": int(frame.loc[mask, "trading_day"].nunique()),
                "mean_abs_trigger_z": float(state.loc[mask, "residual_robust_z"].abs().mean()) if mask.any() else np.nan,
            }
        )

        for horizon in HORIZONS_MINUTES:
            event_return = diagnostic_event_return(
                frame,
                signal,
                holding_bars=horizon // base_cfg.bar_minutes,
                same_trading_day=True,
            )
            event_parts.append(
                pd.DataFrame(
                    {
                        "strategy": "MR_ROBUST_REENTRY",
                        "symbol": symbol,
                        "horizon_minutes": horizon,
                        "market_time_shanghai": frame.loc[mask, "market_time_shanghai"].astype(str),
                        "trading_day": frame.loc[mask, "trading_day"].astype(str),
                        "year": pd.to_datetime(frame.loc[mask, "trading_day"]).dt.year.to_numpy(),
                        "signal": signal.loc[mask].to_numpy(),
                        "event_return": event_return.loc[mask].to_numpy(),
                        "residual_robust_z": state.loc[mask, "residual_robust_z"].to_numpy(),
                        "prior_residual_scale": state.loc[mask, "prior_residual_scale"].to_numpy(),
                    }
                )
            )

    events = pd.concat(event_parts, ignore_index=True)
    counts_df = pd.DataFrame(counts)
    summary = summarize(events)

    events.to_csv(OUT / "events.csv", index=False)
    counts_df.to_csv(OUT / "counts.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    compact = summary.loc[
        (summary["year"].astype(str) == "ALL") & (summary["side"] == "ALL"),
        [
            "strategy",
            "symbol",
            "horizon_minutes",
            "valid_events",
            "mean_return_bps",
            "median_return_bps",
            "win_rate",
        ],
    ].sort_values(["symbol", "horizon_minutes"])

    print("=== v0.5 ROBUST RESIDUAL COUNTS ===")
    print(counts_df.to_string(index=False))
    print("=== v0.5 ROBUST RESIDUAL REENTRY RESULTS ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
