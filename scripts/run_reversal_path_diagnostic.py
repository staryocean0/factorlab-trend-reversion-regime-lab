"""Diagnose path anatomy of the frozen v0.1 reversal/MR signals.

This script does not change the v0.1 signal definitions. It asks whether a
short-lived reversion exists before the negative 30/60/120m terminal outcomes,
and whether favorable excursion is monetizable before adverse continuation.
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
    mean_reversion_signal,
    trend_reversal_signal,
)

OUT = Path("artifacts/reversal_path_diagnostic_v0_2")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
HORIZONS_MINUTES = [5, 10, 15, 30, 60, 120]


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


def future_path_outcomes(
    frame: pd.DataFrame,
    features: pd.DataFrame,
    signal: pd.Series,
    *,
    horizon_bars: int,
) -> pd.DataFrame:
    open_ = pd.to_numeric(frame["open"], errors="coerce").astype(float)
    high = pd.to_numeric(frame["high"], errors="coerce").astype(float)
    low = pd.to_numeric(frame["low"], errors="coerce").astype(float)
    close = pd.to_numeric(frame["close"], errors="coerce").astype(float)
    day = frame["trading_day"].astype(str)

    entry = open_.shift(-1)
    terminal_close = close.shift(-horizon_bars)
    future_high = pd.concat([high.shift(-k) for k in range(1, horizon_bars + 1)], axis=1).max(axis=1)
    future_low = pd.concat([low.shift(-k) for k in range(1, horizon_bars + 1)], axis=1).min(axis=1)

    valid = day.shift(-1).eq(day) & day.shift(-horizon_bars).eq(day) & signal.ne(0)

    signed_terminal = signal.astype(float) * (terminal_close / entry - 1.0)
    mfe = pd.Series(np.nan, index=frame.index, dtype=float)
    mae = pd.Series(np.nan, index=frame.index, dtype=float)
    long = signal.gt(0)
    short = signal.lt(0)
    mfe.loc[long] = future_high.loc[long] / entry.loc[long] - 1.0
    mae.loc[long] = 1.0 - future_low.loc[long] / entry.loc[long]
    mfe.loc[short] = 1.0 - future_low.loc[short] / entry.loc[short]
    mae.loc[short] = future_high.loc[short] / entry.loc[short] - 1.0

    anchor = pd.to_numeric(features["anchor"], errors="coerce")
    initial_distance = (close - anchor).abs()
    terminal_distance = (terminal_close - anchor).abs()
    anchor_progress = 1.0 - terminal_distance / initial_distance.replace(0, np.nan)

    anchor_hit = pd.Series(False, index=frame.index)
    first_anchor_hit = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    first_5bps_hit = pd.Series(pd.NA, index=frame.index, dtype="Int64")
    first_10bps_hit = pd.Series(pd.NA, index=frame.index, dtype="Int64")

    for k in range(1, horizon_bars + 1):
        fh = high.shift(-k)
        fl = low.shift(-k)
        same_day = day.shift(-k).eq(day)
        hit_anchor = same_day & (
            (signal.gt(0) & fh.ge(anchor)) | (signal.lt(0) & fl.le(anchor))
        )
        choose_anchor = signal.ne(0) & first_anchor_hit.isna() & hit_anchor
        first_anchor_hit.loc[choose_anchor] = k
        anchor_hit |= hit_anchor

        favorable = pd.Series(np.nan, index=frame.index, dtype=float)
        favorable.loc[long] = fh.loc[long] / entry.loc[long] - 1.0
        favorable.loc[short] = 1.0 - fl.loc[short] / entry.loc[short]
        hit5 = same_day & favorable.ge(0.0005)
        hit10 = same_day & favorable.ge(0.0010)
        choose5 = signal.ne(0) & first_5bps_hit.isna() & hit5
        choose10 = signal.ne(0) & first_10bps_hit.isna() & hit10
        first_5bps_hit.loc[choose5] = k
        first_10bps_hit.loc[choose10] = k

    # Event onset is a structural de-duplication diagnostic, not a new signal rule.
    same_prev_day = day.shift(1).eq(day)
    same_prev_signal = signal.shift(1).eq(signal)
    onset = signal.ne(0) & ~(same_prev_day & same_prev_signal)

    out = pd.DataFrame(
        {
            "valid": valid,
            "terminal_return": signed_terminal.where(valid),
            "mfe": mfe.where(valid),
            "mae": mae.where(valid),
            "anchor_progress": anchor_progress.where(valid),
            "anchor_hit": anchor_hit.where(valid, False),
            "first_anchor_hit_bars": first_anchor_hit.where(valid),
            "first_5bps_hit_bars": first_5bps_hit.where(valid),
            "first_10bps_hit_bars": first_10bps_hit.where(valid),
            "event_onset": onset,
        }
    )
    return out


def summarize(events: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_keys = ["strategy", "symbol", "horizon_minutes", "scope", "side"]
    for keys, g in events.groupby(group_keys, observed=True):
        valid = g.loc[g["valid"]]
        r = valid["terminal_return"].dropna()
        mfe = valid["mfe"].dropna()
        mae = valid["mae"].dropna()
        progress = valid["anchor_progress"].dropna()
        rows.append(
            {
                **dict(zip(group_keys, keys)),
                "events": int(len(g)),
                "valid_events": int(len(valid)),
                "mean_terminal_bps": float(r.mean() * 1e4) if len(r) else np.nan,
                "median_terminal_bps": float(r.median() * 1e4) if len(r) else np.nan,
                "terminal_win_rate": float((r > 0).mean()) if len(r) else np.nan,
                "median_mfe_bps": float(mfe.median() * 1e4) if len(mfe) else np.nan,
                "median_mae_bps": float(mae.median() * 1e4) if len(mae) else np.nan,
                "p_mfe_ge_5bps": float((mfe >= 0.0005).mean()) if len(mfe) else np.nan,
                "p_mfe_ge_10bps": float((mfe >= 0.0010).mean()) if len(mfe) else np.nan,
                "anchor_hit_rate": float(valid["anchor_hit"].mean()) if len(valid) else np.nan,
                "median_anchor_progress": float(progress.median()) if len(progress) else np.nan,
                "p_anchor_progress_positive": float((progress > 0).mean()) if len(progress) else np.nan,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    cfg = ReversalFeatureConfig()
    event_parts = []

    for symbol in SYMBOLS:
        raw = load_market_data(symbol, "5m", START, END)
        frame = raw.loc[continuous_auction(raw) & strict_quality_mask(raw)].copy().reset_index(drop=True)
        features = compute_reversal_features(frame, cfg)
        mr0 = mean_reversion_signal(features, stretch_threshold=2.0)
        signals = {
            "MR0": mr0,
            "MR1": mean_reversion_signal(
                features,
                stretch_threshold=2.0,
                require_failed_acceptance=True,
            ),
            "REV0": trend_reversal_signal(
                features,
                min_leg_efficiency=0.60,
                min_leg_displacement_atr=1.50,
            ),
        }

        for strategy, signal in signals.items():
            signal_mask = signal.ne(0)
            for horizon in HORIZONS_MINUTES:
                path = future_path_outcomes(
                    frame,
                    features,
                    signal,
                    horizon_bars=horizon // cfg.bar_minutes,
                )
                part = pd.DataFrame(
                    {
                        "strategy": strategy,
                        "symbol": symbol,
                        "horizon_minutes": horizon,
                        "market_time_shanghai": frame.loc[signal_mask, "market_time_shanghai"].astype(str),
                        "trading_day": frame.loc[signal_mask, "trading_day"].astype(str),
                        "year": pd.to_datetime(frame.loc[signal_mask, "trading_day"]).dt.year.to_numpy(),
                        "signal": signal.loc[signal_mask].to_numpy(),
                        "stretch_atr": features.loc[signal_mask, "stretch_atr"].to_numpy(),
                        "leg_efficiency": features.loc[signal_mask, "leg_efficiency"].to_numpy(),
                        "leg_displacement_atr": features.loc[signal_mask, "leg_displacement_atr"].to_numpy(),
                        "shock_concentration": features.loc[signal_mask, "shock_concentration"].to_numpy(),
                    }
                )
                for col in path.columns:
                    part[col] = path.loc[signal_mask, col].to_numpy()
                event_parts.append(part)

    events = pd.concat(event_parts, ignore_index=True)
    events.to_csv(OUT / "path_events.csv", index=False)

    expanded = []
    for scope, mask in {
        "ALL": pd.Series(True, index=events.index),
        "ONSET_ONLY": events["event_onset"].fillna(False).astype(bool),
    }.items():
        x = events.loc[mask].copy()
        x["scope"] = scope
        x["side"] = np.where(x["signal"] > 0, "LONG", "SHORT")
        expanded.append(x)
        y = x.copy()
        y["side"] = "ALL"
        expanded.append(y)
    summary = summarize(pd.concat(expanded, ignore_index=True))
    summary.to_csv(OUT / "path_summary.csv", index=False)

    compact = summary.loc[
        (summary["scope"] == "ALL") & (summary["side"] == "ALL"),
        [
            "strategy",
            "symbol",
            "horizon_minutes",
            "valid_events",
            "mean_terminal_bps",
            "median_terminal_bps",
            "terminal_win_rate",
            "median_mfe_bps",
            "median_mae_bps",
            "p_mfe_ge_5bps",
            "anchor_hit_rate",
            "median_anchor_progress",
        ],
    ].sort_values(["strategy", "symbol", "horizon_minutes"])

    print("=== REVERSAL PATH DIAGNOSTIC v0.2 ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
