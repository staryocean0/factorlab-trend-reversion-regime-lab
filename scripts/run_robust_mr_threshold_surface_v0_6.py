"""Coarse preregistered severity surface for robust-residual MR re-entry.

This is not a winner search. It tests one monotonic mechanism: if a residual
extreme is genuinely a mean-reversion setup, does re-entry after more severe
extremes improve subsequent fade returns? All threshold cells are reported.
2025 remains unopened.
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

OUT = Path("artifacts/robust_mr_threshold_surface_v0_6")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
THRESHOLDS = [2.0, 2.5, 3.0]
HORIZONS_MINUTES = [5, 10, 15, 30, 60, 120]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (threshold, symbol, horizon), g in events.groupby(
        ["threshold", "symbol", "horizon_minutes"]
    ):
        r = g["event_return"].dropna()
        if len(r):
            q05 = r.quantile(0.05)
            q95 = r.quantile(0.95)
            central = r[(r > q05) & (r < q95)]
        else:
            q05 = q95 = np.nan
            central = r
        rows.append(
            {
                "threshold": threshold,
                "symbol": symbol,
                "horizon_minutes": horizon,
                "events": int(len(g)),
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
    base_cfg = ReversalFeatureConfig()
    event_parts = []
    counts = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        frame = raw.loc[continuous_auction(raw)].copy().reset_index(drop=True)
        base = compute_reversal_features(frame, base_cfg)

        # Distribution estimate itself is identical across threshold cells.
        state_cfg = RobustResidualConfig(
            bar_minutes=5,
            distribution_minutes=240,
            threshold=2.0,
        )
        state = compute_robust_residual_state(frame, base, state_cfg)

        for threshold in THRESHOLDS:
            cfg = RobustResidualConfig(
                bar_minutes=5,
                distribution_minutes=240,
                threshold=threshold,
            )
            signal = robust_residual_reentry_signal(frame, state, cfg)
            mask = signal.ne(0)
            # Severity is the prior-bar z that was actually outside the band.
            prior_abs_z = state["residual_robust_z"].shift(1).abs()
            counts.append(
                {
                    "threshold": threshold,
                    "symbol": symbol,
                    "signal_bars": int(mask.sum()),
                    "signal_days": int(frame.loc[mask, "trading_day"].nunique()),
                    "median_prior_abs_z": float(prior_abs_z.loc[mask].median()) if mask.any() else np.nan,
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
                            "threshold": threshold,
                            "symbol": symbol,
                            "horizon_minutes": horizon,
                            "trading_day": frame.loc[mask, "trading_day"].astype(str),
                            "signal": signal.loc[mask].to_numpy(),
                            "prior_abs_z": prior_abs_z.loc[mask].to_numpy(),
                            "event_return": event_return.loc[mask].to_numpy(),
                        }
                    )
                )

    events = pd.concat(event_parts, ignore_index=True)
    counts_df = pd.DataFrame(counts)
    summary = summarize(events).sort_values(["symbol", "horizon_minutes", "threshold"])

    events.to_csv(OUT / "events.csv", index=False)
    counts_df.to_csv(OUT / "counts.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)

    print("=== v0.6 SEVERITY COUNTS ===")
    print(counts_df.to_string(index=False))
    print("=== v0.6 ROBUST MR SEVERITY SURFACE ===")
    print(summary.to_string(index=False))

    # Mechanism diagnostic only: report whether mean return improves strictly
    # from 2.0 -> 2.5 -> 3.0 for every horizon within each symbol.
    monotonic = []
    for symbol in SYMBOLS:
        for horizon in HORIZONS_MINUTES:
            x = summary.loc[
                (summary["symbol"] == symbol)
                & (summary["horizon_minutes"] == horizon)
            ].sort_values("threshold")
            vals = x["mean_return_bps"].to_numpy()
            monotonic.append(
                {
                    "symbol": symbol,
                    "horizon_minutes": horizon,
                    "strict_mean_improvement": bool(np.all(np.diff(vals) > 0)),
                }
            )
    monotonic_df = pd.DataFrame(monotonic)
    monotonic_df.to_csv(OUT / "monotonicity.csv", index=False)
    print("=== STRICT MEAN MONOTONICITY ===")
    print(monotonic_df.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
