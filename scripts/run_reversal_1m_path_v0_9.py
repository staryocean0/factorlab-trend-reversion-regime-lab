"""v0.9: Resolve the first 5m bar of the frozen 5m MR signal using 1m paths.

The signal definition is unchanged from v0.5/v0.8 and is computed only on 5m
bars. We then project the completed 5m signal timestamp onto the supplied 1m
bars. Entry is the next 1m open, which should equal the next 5m bar open. The
purpose is not to create a new 1m strategy; it is to resolve target/stop ordering
that is unknowable inside a 5m OHLC bar.

2025 remains unopened. All results are gross index diagnostics.
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

OUT = Path("artifacts/reversal_1m_path_v0_9")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOLS = ["000688.SH", "000852.SH"]
START = "2020-07-23"
END = "2024-12-31"
BARRIER_BPS = [5.0, 10.0]
HORIZONS_MINUTES = [5, 10, 30]


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
        source_count = pd.to_numeric(frame["source_minute_count"], errors="coerce")
        mask &= source_count.ge(expected_source_minutes)
    return mask


def _project_5m_signal_to_1m(
    frame5: pd.DataFrame,
    signal5: pd.Series,
    frame1: pd.DataFrame,
) -> pd.Series:
    mapping = pd.Series(signal5.to_numpy(), index=frame5["market_time_shanghai"])
    projected = frame1["market_time_shanghai"].map(mapping).fillna(0).astype("int8")
    return projected


def _entry_alignment_audit(
    frame5: pd.DataFrame,
    signal5: pd.Series,
    frame1: pd.DataFrame,
) -> dict:
    next_1m_open = pd.Series(
        pd.to_numeric(frame1["open"], errors="coerce").shift(-1).to_numpy(),
        index=frame1["market_time_shanghai"],
    )
    sig = signal5.ne(0)
    same_day5 = frame5["trading_day"].shift(-1).eq(frame5["trading_day"])
    idx = sig & same_day5
    times = frame5.loc[idx, "market_time_shanghai"]
    entry5 = pd.to_numeric(frame5["open"], errors="coerce").shift(-1).loc[idx].to_numpy()
    entry1 = times.map(next_1m_open).to_numpy(dtype=float)
    finite = np.isfinite(entry5) & np.isfinite(entry1)
    diffs = np.abs(entry5[finite] - entry1[finite])
    return {
        "entry_audit_events": int(finite.sum()),
        "entry_exact_match_rate": float(np.mean(diffs == 0.0)) if len(diffs) else np.nan,
        "entry_max_abs_point_diff": float(np.max(diffs)) if len(diffs) else np.nan,
    }


def main() -> None:
    feature_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(threshold=2.0)
    audits = []
    event_parts = []
    summary_parts = []

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
        signal1 = _project_5m_signal_to_1m(frame5, signal5, frame1)
        prior_z5 = pd.to_numeric(state5["residual_robust_z"], errors="coerce").shift(1)
        prior_z_map = pd.Series(prior_z5.to_numpy(), index=frame5["market_time_shanghai"])
        prior_z1 = frame1["market_time_shanghai"].map(prior_z_map)

        mapped_signal_count = int(signal1.ne(0).sum())
        entry_audit = _entry_alignment_audit(frame5, signal5, frame1)
        audits.append(
            {
                "symbol": symbol,
                "rows_5m": len(frame5),
                "rows_1m": len(frame1),
                "days_5m": frame5["trading_day"].nunique(),
                "days_1m": frame1["trading_day"].nunique(),
                "signals_5m": int(signal5.ne(0).sum()),
                "signals_mapped_to_1m": mapped_signal_count,
                **entry_audit,
            }
        )

        for barrier in BARRIER_BPS:
            # Define the exact v0.8 ambiguity set on 5m, using the 30m cap.
            path5 = symmetric_first_passage(
                frame5,
                signal5,
                barrier_bps=barrier,
                horizon_bars=30 // robust_cfg.bar_minutes,
            )
            ambiguous5 = path5["valid"].fillna(False).astype(bool) & path5["outcome"].eq(
                "ambiguous_same_bar"
            )
            ambiguous_times = set(frame5.loc[ambiguous5, "market_time_shanghai"])

            for horizon in HORIZONS_MINUTES:
                path1 = symmetric_first_passage(
                    frame1,
                    signal1,
                    barrier_bps=barrier,
                    horizon_bars=horizon,
                )
                valid = path1["valid"].fillna(False).astype(bool)
                signal_times = frame1.loc[valid, "market_time_shanghai"]
                source_class = np.where(
                    signal_times.isin(ambiguous_times),
                    "5M_AMBIGUOUS",
                    "5M_NON_AMBIGUOUS",
                )
                events = pd.DataFrame(
                    {
                        "symbol": symbol,
                        "barrier_bps": barrier,
                        "horizon_minutes": horizon,
                        "market_time_shanghai": signal_times.astype(str).to_numpy(),
                        "trading_day": frame1.loc[valid, "trading_day"].astype(str).to_numpy(),
                        "signal": signal1.loc[valid].to_numpy(),
                        "side": np.where(signal1.loc[valid].to_numpy() > 0, "LONG", "SHORT"),
                        "source_5m_class": source_class,
                        "prior_extreme_z": prior_z1.loc[valid].to_numpy(),
                        "entry_price": path1.loc[valid, "entry_price"].to_numpy(),
                        "outcome": path1.loc[valid, "outcome"].astype(str).to_numpy(),
                        "resolution_minutes": path1.loc[valid, "resolution_bars"].to_numpy(),
                    }
                )
                # summarize_first_passage expects the generic column name.
                summary_input = events.rename(columns={"resolution_minutes": "resolution_bars"})
                event_parts.append(events)

                groups = {
                    "ALL": summary_input,
                    "5M_AMBIGUOUS_ONLY": summary_input.loc[
                        summary_input["source_5m_class"].eq("5M_AMBIGUOUS")
                    ],
                }
                for subset_name, subset in groups.items():
                    s = summarize_first_passage(subset)
                    s = s.rename(
                        columns={
                            "median_bars_to_target": "median_minutes_to_target",
                            "median_bars_to_stop": "median_minutes_to_stop",
                        }
                    )
                    s.insert(0, "subset", subset_name)
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
        summary["subset"].isin(["ALL", "5M_AMBIGUOUS_ONLY"]),
        [
            "symbol",
            "barrier_bps",
            "horizon_minutes",
            "subset",
            "events",
            "target_first_rate",
            "stop_first_rate",
            "ambiguous_rate",
            "neither_rate",
            "target_share_clean_resolutions",
            "target_share_ambiguous_as_adverse",
            "median_minutes_to_target",
            "median_minutes_to_stop",
        ],
    ].sort_values(["symbol", "barrier_bps", "horizon_minutes", "subset"])

    print("=== v0.9 5m-SIGNAL / 1m-PATH AUDIT ===")
    print(audit.to_string(index=False))
    print("=== v0.9 1m TARGET-vs-STOP FIRST PASSAGE ===")
    print(compact.to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
