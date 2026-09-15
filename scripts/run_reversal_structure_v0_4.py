"""Test stronger reversal geometry after v0.1-v0.3 failures.

MR_REENTRY changes the MR event from fading while extreme to entering only after
stretch crosses back inside the same frozen 2-ATR band.
REV_STRUCT keeps the REV0 candidate and requires the next completed close to
break the failed-breakout bar's opposite extreme.
No trend-following strategy is evaluated. 2025 remains unopened.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.market_data import load_market_data
from regime_lab.reversal_confirmations import (
    mean_reversion_reentry_signal,
    structural_reversal_confirmation,
)
from regime_lab.reversal_mean_reversion import (
    ReversalFeatureConfig,
    compute_reversal_features,
    diagnostic_event_return,
    trend_reversal_signal,
)

OUT = Path("artifacts/reversal_structure_v0_4")
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
    for (strategy, symbol, horizon), base in events.groupby(
        ["strategy", "symbol", "horizon_minutes"]
    ):
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
                        "strategy": strategy,
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
    cfg = ReversalFeatureConfig()
    event_parts = []
    counts = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        frame = raw.loc[continuous_auction(raw)].copy().reset_index(drop=True)
        features = compute_reversal_features(frame, cfg)

        rev0 = trend_reversal_signal(
            features,
            min_leg_efficiency=0.60,
            min_leg_displacement_atr=1.50,
        )
        signals = {
            "MR_REENTRY": mean_reversion_reentry_signal(
                frame,
                features,
                stretch_threshold=2.0,
            ),
            "REV_STRUCT": structural_reversal_confirmation(frame, rev0),
        }

        for strategy, signal in signals.items():
            counts.append(
                {
                    "strategy": strategy,
                    "symbol": symbol,
                    "signal_bars": int(signal.ne(0).sum()),
                }
            )
            mask = signal.ne(0)
            for horizon in HORIZONS_MINUTES:
                event_return = diagnostic_event_return(
                    frame,
                    signal,
                    holding_bars=horizon // cfg.bar_minutes,
                    same_trading_day=True,
                )
                event_parts.append(
                    pd.DataFrame(
                        {
                            "strategy": strategy,
                            "symbol": symbol,
                            "horizon_minutes": horizon,
                            "market_time_shanghai": frame.loc[mask, "market_time_shanghai"].astype(str),
                            "trading_day": frame.loc[mask, "trading_day"].astype(str),
                            "year": pd.to_datetime(frame.loc[mask, "trading_day"]).dt.year.to_numpy(),
                            "signal": signal.loc[mask].to_numpy(),
                            "event_return": event_return.loc[mask].to_numpy(),
                        }
                    )
                )

    events = pd.concat(event_parts, ignore_index=True)
    counts_df = pd.DataFrame(counts)
    summary = summarize(events)
    events.to_csv(OUT / "structure_events.csv", index=False)
    counts_df.to_csv(OUT / "structure_counts.csv", index=False)
    summary.to_csv(OUT / "structure_summary.csv", index=False)

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
    ].sort_values(["strategy", "symbol", "horizon_minutes"])

    print("=== v0.4 SIGNAL COUNTS ===")
    print(counts_df.to_string(index=False))
    print("=== v0.4 REENTRY / STRUCTURAL REVERSAL RESULTS ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
