"""Run the first STAR50-vs-CSI1000 relative-value MR baseline.

Mechanism: 60-trading-minute STAR-minus-CSI relative return dislocation,
standardized by the most recent 48 valid prior dislocation observations; enter
only after z re-enters from outside +/-2.0. Equal-notional two-leg diagnostic
entry is next bar open. No trend filter. 2025 remains unopened.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.market_data import load_market_data
from regime_lab.relative_mean_reversion import (
    RelativeMRConfig,
    align_pair,
    compute_relative_state,
    relative_diagnostic_return,
    relative_reentry_signal,
)

OUT = Path("artifacts/relative_mean_reversion_v0_7")
OUT.mkdir(parents=True, exist_ok=True)

START = "2020-07-23"
END = "2024-12-31"
HORIZONS_MINUTES = [5, 10, 15, 30, 60, 120]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    years = sorted(events["year"].dropna().astype(int).unique().tolist())
    for horizon, base in events.groupby("horizon_minutes"):
        for year in ["ALL", *years]:
            g = base if year == "ALL" else base.loc[base["year"] == year]
            for side in ["ALL", "LONG_STAR", "SHORT_STAR"]:
                x = g
                if side == "LONG_STAR":
                    x = g.loc[g["signal"] > 0]
                elif side == "SHORT_STAR":
                    x = g.loc[g["signal"] < 0]
                r = x["event_return"].dropna()
                if len(r):
                    q05 = r.quantile(0.05)
                    q95 = r.quantile(0.95)
                    central = r[(r > q05) & (r < q95)]
                else:
                    q05 = q95 = np.nan
                    central = r
                rows.append(
                    {
                        "strategy": "REL_MR_REENTRY",
                        "horizon_minutes": int(horizon),
                        "year": year,
                        "side": side,
                        "events": int(len(x)),
                        "valid_events": int(len(r)),
                        "mean_return_bps": float(r.mean() * 1e4) if len(r) else np.nan,
                        "median_return_bps": float(r.median() * 1e4) if len(r) else np.nan,
                        "win_rate": float((r > 0).mean()) if len(r) else np.nan,
                        "p05_return_bps": float(q05 * 1e4) if len(r) else np.nan,
                        "p95_return_bps": float(q95 * 1e4) if len(r) else np.nan,
                        "central_90_mean_bps": float(central.mean() * 1e4) if len(central) else np.nan,
                    }
                )
    return pd.DataFrame(rows)


def main() -> None:
    star_raw = load_market_data("000688.SH", "5m", START, END)
    csi_raw = load_market_data("000852.SH", "5m", START, END)
    star = star_raw.loc[continuous_auction(star_raw)].copy().reset_index(drop=True)
    csi = csi_raw.loc[continuous_auction(csi_raw)].copy().reset_index(drop=True)
    pair = align_pair(star, csi)

    cfg = RelativeMRConfig(
        bar_minutes=5,
        dislocation_minutes=60,
        distribution_minutes=240,
        threshold=2.0,
    )
    state = compute_relative_state(pair, cfg)
    signal = relative_reentry_signal(pair, state, cfg)
    mask = signal.ne(0)

    audit = pd.DataFrame(
        [
            {
                "star_rows": len(star),
                "csi_rows": len(csi),
                "paired_rows": len(pair),
                "paired_days": int(pair["trading_day"].nunique()),
                "first_time": str(pair["market_time_shanghai"].min()),
                "last_time": str(pair["market_time_shanghai"].max()),
                "valid_relative_move_rows": int(state["relative_move"].notna().sum()),
                "valid_z_rows": int(state["relative_robust_z"].notna().sum()),
                "signal_bars": int(mask.sum()),
                "signal_days": int(pair.loc[mask, "trading_day"].nunique()),
                "long_star_signals": int((signal > 0).sum()),
                "short_star_signals": int((signal < 0).sum()),
            }
        ]
    )
    audit.to_csv(OUT / "audit.csv", index=False)

    parts = []
    for horizon in HORIZONS_MINUTES:
        r = relative_diagnostic_return(
            pair,
            signal,
            holding_bars=horizon // cfg.bar_minutes,
        )
        parts.append(
            pd.DataFrame(
                {
                    "strategy": "REL_MR_REENTRY",
                    "horizon_minutes": horizon,
                    "market_time_shanghai": pair.loc[mask, "market_time_shanghai"].astype(str),
                    "trading_day": pair.loc[mask, "trading_day"].astype(str),
                    "year": pd.to_datetime(pair.loc[mask, "trading_day"]).dt.year.to_numpy(),
                    "signal": signal.loc[mask].to_numpy(),
                    "relative_robust_z": state.loc[mask, "relative_robust_z"].to_numpy(),
                    "prior_relative_z": state["relative_robust_z"].shift(1).loc[mask].to_numpy(),
                    "relative_move": state.loc[mask, "relative_move"].to_numpy(),
                    "event_return": r.loc[mask].to_numpy(),
                }
            )
        )

    events = pd.concat(parts, ignore_index=True)
    summary = summarize(events)
    events.to_csv(OUT / "events.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    compact = summary.loc[
        (summary["year"].astype(str) == "ALL") & (summary["side"] == "ALL"),
        [
            "strategy",
            "horizon_minutes",
            "valid_events",
            "mean_return_bps",
            "median_return_bps",
            "win_rate",
            "central_90_mean_bps",
        ],
    ].sort_values("horizon_minutes")

    print("=== v0.7 PAIR AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.7 RELATIVE-VALUE MR RESULTS ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
