"""Run the unchanged v0.1 MR0/REV0 baseline on consumed 5m history.

This is a research diagnostic, not a production backtest. It intentionally
uses 2020-2024 only; 2025 remains unopened by this phase-1 baseline runner.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.market_data import load_market_data
from regime_lab.reversal_mean_reversion import (
    ReversalFeatureConfig,
    compute_reversal_features,
    diagnostic_event_return,
    frozen_anchor_hit_bars,
    mean_reversion_signal,
    trend_reversal_signal,
)

OUT = Path("artifacts/reversal_baseline_v0_1")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
HOLDING_MINUTES = [30, 60, 120]


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    morning = minute.between(9 * 60 + 30, 11 * 60 + 30)
    afternoon = minute.between(13 * 60, 15 * 60)
    return morning | afternoon


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


def summarize(
    events: pd.DataFrame,
    *,
    strategy: str,
    symbol: str,
    holding_minutes: int,
    year: int | str,
    side: str,
) -> dict:
    x = events.loc[
        (events["strategy"] == strategy)
        & (events["symbol"] == symbol)
        & (events["holding_minutes"] == holding_minutes)
    ].copy()
    if year != "ALL":
        x = x.loc[x["year"] == int(year)]
    if side == "LONG":
        x = x.loc[x["signal"] > 0]
    elif side == "SHORT":
        x = x.loc[x["signal"] < 0]

    valid = x["valid_horizon"].fillna(False).astype(bool)
    xv = x.loc[valid]
    r = xv["event_return"].dropna()
    hits = xv["anchor_hit_bars"].notna()
    hit_bars = pd.to_numeric(xv.loc[hits, "anchor_hit_bars"], errors="coerce")

    return {
        "strategy": strategy,
        "symbol": symbol,
        "holding_minutes": holding_minutes,
        "year": year,
        "side": side,
        "events": int(len(x)),
        "valid_horizon_events": int(valid.sum()),
        "mean_return_bps": float(r.mean() * 1e4) if len(r) else np.nan,
        "median_return_bps": float(r.median() * 1e4) if len(r) else np.nan,
        "win_rate": float((r > 0).mean()) if len(r) else np.nan,
        "p05_return_bps": float(r.quantile(0.05) * 1e4) if len(r) else np.nan,
        "p95_return_bps": float(r.quantile(0.95) * 1e4) if len(r) else np.nan,
        "anchor_hit_rate": float(hits.mean()) if len(xv) else np.nan,
        "median_anchor_hit_bars": float(hit_bars.median()) if len(hit_bars) else np.nan,
        "mean_abs_stretch_atr": float(xv["stretch_atr"].abs().mean()) if len(xv) else np.nan,
        "mean_leg_efficiency": float(xv["leg_efficiency"].mean()) if len(xv) else np.nan,
        "mean_shock_concentration": float(xv["shock_concentration"].mean()) if len(xv) else np.nan,
    }


def main() -> None:
    cfg = ReversalFeatureConfig()
    all_events = []
    audit_rows = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        before = len(raw)
        session = continuous_auction(raw)
        quality = strict_quality_mask(raw)
        frame = raw.loc[session & quality].copy().reset_index(drop=True)

        audit_rows.append(
            {
                "symbol": symbol,
                "raw_rows": before,
                "continuous_auction_rows": int(session.sum()),
                "strict_quality_rows": len(frame),
                "columns": "|".join(frame.columns),
                "first_time": str(frame["market_time_shanghai"].min()),
                "last_time": str(frame["market_time_shanghai"].max()),
                "days": int(frame["trading_day"].nunique()),
            }
        )

        features = compute_reversal_features(frame, cfg)
        signals = {
            "MR0": mean_reversion_signal(features, stretch_threshold=2.0),
            "REV0": trend_reversal_signal(
                features,
                min_leg_efficiency=0.60,
                min_leg_displacement_atr=1.50,
            ),
        }

        for strategy, signal in signals.items():
            for holding_minutes in HOLDING_MINUTES:
                bars = holding_minutes // cfg.bar_minutes
                event_return = diagnostic_event_return(
                    frame,
                    signal,
                    holding_bars=bars,
                    same_trading_day=True,
                )
                anchor_hit = frozen_anchor_hit_bars(
                    frame,
                    features,
                    signal,
                    max_bars=bars,
                    same_trading_day=True,
                )

                mask = signal.ne(0)
                if not mask.any():
                    continue
                part = pd.DataFrame(
                    {
                        "symbol": symbol,
                        "strategy": strategy,
                        "holding_minutes": holding_minutes,
                        "market_time_shanghai": frame.loc[mask, "market_time_shanghai"].astype(str),
                        "trading_day": frame.loc[mask, "trading_day"].astype(str),
                        "year": pd.to_datetime(frame.loc[mask, "trading_day"]).dt.year.to_numpy(),
                        "signal": signal.loc[mask].to_numpy(),
                        "event_return": event_return.loc[mask].to_numpy(),
                        "valid_horizon": event_return.loc[mask].notna().to_numpy(),
                        "anchor_hit_bars": anchor_hit.loc[mask].astype("Float64").to_numpy(),
                        "stretch_atr": features.loc[mask, "stretch_atr"].to_numpy(),
                        "leg_efficiency": features.loc[mask, "leg_efficiency"].to_numpy(),
                        "leg_displacement_atr": features.loc[mask, "leg_displacement_atr"].to_numpy(),
                        "shock_concentration": features.loc[mask, "shock_concentration"].to_numpy(),
                        "failed_break_above": features.loc[mask, "failed_break_above"].to_numpy(),
                        "failed_break_below": features.loc[mask, "failed_break_below"].to_numpy(),
                    }
                )
                all_events.append(part)

    audit = pd.DataFrame(audit_rows)
    audit.to_csv(OUT / "data_audit.csv", index=False)

    events = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    events.to_csv(OUT / "events.csv", index=False)

    summaries = []
    if not events.empty:
        years = sorted(events["year"].dropna().astype(int).unique().tolist())
        for strategy in ["MR0", "REV0"]:
            for symbol in SYMBOLS:
                for holding in HOLDING_MINUTES:
                    for year in ["ALL", *years]:
                        for side in ["ALL", "LONG", "SHORT"]:
                            summaries.append(
                                summarize(
                                    events,
                                    strategy=strategy,
                                    symbol=symbol,
                                    holding_minutes=holding,
                                    year=year,
                                    side=side,
                                )
                            )

    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "baseline_summary.csv", index=False)

    compact = summary.loc[
        (summary["year"] == "ALL") & (summary["side"] == "ALL"),
        [
            "strategy",
            "symbol",
            "holding_minutes",
            "events",
            "valid_horizon_events",
            "mean_return_bps",
            "median_return_bps",
            "win_rate",
            "anchor_hit_rate",
        ],
    ]
    print("=== DATA AUDIT ===")
    print(audit.to_string(index=False))
    print("=== BASELINE ALL-YEAR / ALL-SIDE ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)

    metadata = {
        "schema": "reversal_baseline_v0_1",
        "symbols": SYMBOLS,
        "frequency": "5m",
        "start": START,
        "end": END,
        "strategies": ["MR0", "REV0"],
        "holding_minutes": HOLDING_MINUTES,
        "note": "consumed historical diagnostic; not fresh OOS; no 2025 opened",
    }
    (OUT / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")


if __name__ == "__main__":
    main()
