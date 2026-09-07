"""v0.14.2: resolve frozen 2025 reversal exit clocks on supplied 3s points.

No predictive rule is changed. The signal remains the v0.13 completed-5m
CSI1000 negative-gap H1 LONG robust residual re-entry. The v0.14.1 execution
architecture still executes only the first qualifying event per trading day.

The 3s source is a point-price observation stream, not OHLC. Therefore this
script never invents intrainterval extrema. It uses 3s points only to narrow
cash-index trigger timestamps when an actual supplied point observes a barrier.
The frozen 1m high/low policy remains the scientific outcome authority.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.barrier_policy import evaluate_barrier_timeout_policy
from regime_lab.market_data import load_market_data
from regime_lab.point_first_passage import resolve_point_first_passage
from regime_lab.reversal_mean_reversion import ReversalFeatureConfig, compute_reversal_features
from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)

OUT = Path("artifacts/reversal_3s_execution_clock_v0_14_2")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOL = "000852.SH"
SIGNAL_START = "2020-07-23"
SIGNAL_END = "2025-12-31"
POINT_START = "2025-01-01"
POINT_END = "2025-12-31"
BARRIER_BPS = 10.0
HORIZON_MINUTES = 10
ENTRY_WINDOW_PRE_SECONDS = 3
ENTRY_WINDOW_POST_SECONDS = 6
EXIT_WINDOW_SECONDS = 6


def continuous_auction(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.between(9 * 60 + 30, 11 * 60 + 30) | minute.between(13 * 60, 15 * 60)


def h1_mask(frame: pd.DataFrame) -> pd.Series:
    t = frame["market_time_shanghai"]
    minute = t.dt.hour * 60 + t.dt.minute
    return minute.ge(9 * 60 + 30) & minute.lt(10 * 60)


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


def daily_gap_map(frame5: pd.DataFrame) -> pd.Series:
    daily = (
        frame5.groupby("trading_day", sort=True)
        .agg(day_open=("open", "first"), day_close=("close", "last"))
        .reset_index()
    )
    daily["prev_close"] = pd.to_numeric(daily["day_close"], errors="coerce").shift(1)
    daily["overnight_gap_log"] = np.log(
        pd.to_numeric(daily["day_open"], errors="coerce") / daily["prev_close"]
    )
    return daily.set_index("trading_day")["overnight_gap_log"]


def exact_point_map(frame3: pd.DataFrame) -> dict[pd.Timestamp, list[float]]:
    out: dict[pd.Timestamp, list[float]] = {}
    for t, g in frame3.groupby("market_time_shanghai", sort=False):
        prices = pd.to_numeric(g["price"], errors="coerce").dropna().astype(float).tolist()
        if prices:
            out[pd.Timestamp(t)] = prices
    return out


def alignment_audit(frame1_2025: pd.DataFrame, frame3: pd.DataFrame) -> pd.DataFrame:
    """Empirically verify the 1m end-label/open-start wall-clock contract."""
    point_map = exact_point_map(frame3)
    rows = []
    for _, r in frame1_2025.iterrows():
        label = pd.Timestamp(r["market_time_shanghai"])
        open_time = label - pd.Timedelta(minutes=1)
        close_time = label
        open_prices = point_map.get(open_time, [])
        close_prices = point_map.get(close_time, [])
        open_ = float(r["open"])
        close = float(r["close"])
        if open_prices:
            rows.append(
                {
                    "field": "1m_open_vs_3s_at_label_minus_1m",
                    "abs_diff": min(abs(open_ - p) for p in open_prices),
                }
            )
        if close_prices:
            rows.append(
                {
                    "field": "1m_close_vs_3s_at_label",
                    "abs_diff": min(abs(close - p) for p in close_prices),
                }
            )
    x = pd.DataFrame(rows)
    if x.empty:
        return pd.DataFrame()
    return (
        x.groupby("field", observed=True)["abs_diff"]
        .agg(
            comparisons="size",
            exact_matches=lambda s: int((s == 0.0).sum()),
            exact_match_rate=lambda s: float((s == 0.0).mean()),
            median_abs_point_diff="median",
            max_abs_point_diff="max",
        )
        .reset_index()
    )


def classify_grid_relation(one_minute_outcome: str, point_outcome: str) -> str:
    if one_minute_outcome == point_outcome:
        return "same_outcome_observed"
    if one_minute_outcome == "time_out" and point_outcome == "no_observed_cross":
        return "timeout_consistent_no_3s_cross"
    if one_minute_outcome in {"target_first", "stop_first", "ambiguous_stop_assumed"} and point_outcome == "no_observed_cross":
        return "1m_extreme_not_observed_on_3s_points"
    return "directionally_discordant"


def main() -> None:
    raw5 = load_market_data(SYMBOL, "5m", SIGNAL_START, SIGNAL_END)
    raw1 = load_market_data(SYMBOL, "1m", SIGNAL_START, SIGNAL_END)
    raw3 = load_market_data(SYMBOL, "3s", POINT_START, POINT_END)

    frame5 = raw5.loc[
        continuous_auction(raw5) & strict_quality_mask(raw5, expected_source_minutes=5)
    ].copy().reset_index(drop=True)
    frame1 = raw1.loc[
        continuous_auction(raw1) & strict_quality_mask(raw1, expected_source_minutes=1)
    ].copy().reset_index(drop=True)
    frame3 = raw3.loc[
        continuous_auction(raw3) & raw3["session_phase"].astype(str).eq("continuous_auction")
    ].copy().reset_index(drop=True)

    feature_cfg = ReversalFeatureConfig()
    robust_cfg = RobustResidualConfig(threshold=2.0)
    features5 = compute_reversal_features(frame5, feature_cfg)
    state5 = compute_robust_residual_state(frame5, features5, robust_cfg)
    signal5 = robust_residual_reentry_signal(frame5, state5, robust_cfg)

    gaps = daily_gap_map(frame5)
    gap5 = frame5["trading_day"].astype(str).map(gaps)
    candidate5 = signal5.eq(1) & h1_mask(frame5) & gap5.lt(0)

    signal_map = pd.Series(signal5.to_numpy(), index=frame5["market_time_shanghai"])
    signal1 = frame1["market_time_shanghai"].map(signal_map).fillna(0).astype("int8")
    gap1 = frame1["trading_day"].astype(str).map(gaps)
    candidate1 = signal1.eq(1) & h1_mask(frame1) & gap1.lt(0) & frame1["market_time_shanghai"].dt.year.eq(2025)

    first_idx = (
        frame1.loc[candidate1, ["trading_day", "market_time_shanghai"]]
        .sort_values(["trading_day", "market_time_shanghai"], kind="stable")
        .groupby("trading_day", sort=False)
        .head(1)
        .index
    )
    execution_signal = pd.Series(0, index=frame1.index, dtype="int8")
    execution_signal.loc[first_idx] = 1

    policy1 = evaluate_barrier_timeout_policy(
        frame1,
        execution_signal,
        barrier_bps=BARRIER_BPS,
        horizon_bars=HORIZON_MINUTES,
    )
    valid = policy1["valid"].fillna(False).astype(bool)
    event_indices = frame1.index[valid]

    frame1_2025 = frame1.loc[frame1["market_time_shanghai"].dt.year.eq(2025)].copy()
    align = alignment_audit(frame1_2025, frame3)
    align.to_csv(OUT / "bar_clock_alignment_audit.csv", index=False)

    point_map = exact_point_map(frame3)
    event_rows = []
    quote_rows = []

    # Prior trading-day map for causal IM contract-selection data requests.
    all_days = frame5[["trading_day"]].drop_duplicates().reset_index(drop=True)
    all_days["prior_trading_day"] = all_days["trading_day"].shift(1)
    prior_day_map = all_days.set_index("trading_day")["prior_trading_day"]

    for idx in event_indices:
        signal_time = pd.Timestamp(frame1.loc[idx, "market_time_shanghai"])
        day = str(frame1.loc[idx, "trading_day"])
        entry_price = float(policy1.loc[idx, "entry_price"])
        one_outcome = str(policy1.loc[idx, "outcome"])
        resolution_min = int(policy1.loc[idx, "resolution_bars"])
        end_time = signal_time + pd.Timedelta(minutes=HORIZON_MINUTES)

        day_points = frame3.loc[frame3["trading_day"].astype(str).eq(day)]
        p = resolve_point_first_passage(
            day_points,
            entry_time=signal_time,
            end_time=end_time,
            entry_price=entry_price,
            direction=1,
            barrier_bps=BARRIER_BPS,
        )
        relation = classify_grid_relation(one_outcome, p.outcome)

        entry_obs = point_map.get(signal_time, [])
        entry_abs_diff = min((abs(entry_price - q) for q in entry_obs), default=np.nan)
        entry_exact = bool(entry_abs_diff == 0.0) if np.isfinite(entry_abs_diff) else False

        minute_interval_start = signal_time + pd.Timedelta(minutes=max(resolution_min - 1, 0))
        minute_interval_end = signal_time + pd.Timedelta(minutes=resolution_min)

        if p.trigger_time is not None:
            exit_center = p.trigger_time
            exit_window_start = exit_center - pd.Timedelta(seconds=EXIT_WINDOW_SECONDS)
            exit_window_end = exit_center + pd.Timedelta(seconds=EXIT_WINDOW_SECONDS)
            exit_window_basis = "3s_observed_crossing"
        elif one_outcome == "time_out":
            exit_center = end_time
            exit_window_start = exit_center - pd.Timedelta(seconds=EXIT_WINDOW_SECONDS)
            exit_window_end = exit_center + pd.Timedelta(seconds=EXIT_WINDOW_SECONDS)
            exit_window_basis = "frozen_10m_timeout"
        else:
            # 1m native OHLC saw a barrier, but supplied point sampling did not.
            # Request the full native-resolution minute rather than inventing a
            # precise 3s trigger.
            exit_center = pd.NaT
            exit_window_start = minute_interval_start - pd.Timedelta(seconds=3)
            exit_window_end = minute_interval_end + pd.Timedelta(seconds=3)
            exit_window_basis = "1m_resolution_interval_3s_unobserved"

        target_level = entry_price * (1.0 + BARRIER_BPS / 1e4)
        stop_level = entry_price * (1.0 - BARRIER_BPS / 1e4)

        event_rows.append(
            {
                "trading_day": day,
                "signal_time": signal_time,
                "entry_physical_time": signal_time,
                "entry_price_frozen_1m_open": entry_price,
                "entry_exact_3s_price_available": entry_exact,
                "entry_3s_min_abs_point_diff": entry_abs_diff,
                "target_level": target_level,
                "stop_level": stop_level,
                "one_minute_outcome": one_outcome,
                "one_minute_resolution_minute": resolution_min,
                "one_minute_resolution_interval_start": minute_interval_start,
                "one_minute_resolution_interval_end": minute_interval_end,
                "point_3s_outcome": p.outcome,
                "point_3s_trigger_time": p.trigger_time,
                "point_3s_trigger_price": p.trigger_price,
                "point_3s_observed_points_in_window": p.observed_points,
                "grid_relation": relation,
                "exit_quote_window_basis": exit_window_basis,
                "exit_quote_window_start": exit_window_start,
                "exit_quote_window_end": exit_window_end,
                "frozen_1m_gross_policy_bps": float(policy1.loc[idx, "gross_policy_bps"]),
            }
        )
        quote_rows.append(
            {
                "trading_day": day,
                "prior_trading_day_for_contract_selection": prior_day_map.get(day, pd.NA),
                "entry_bbo_window_start": signal_time - pd.Timedelta(seconds=ENTRY_WINDOW_PRE_SECONDS),
                "entry_bbo_window_end": signal_time + pd.Timedelta(seconds=ENTRY_WINDOW_POST_SECONDS),
                "entry_action": "BUY_CLOSE_PRIOR_DAY_IM_SHORT",
                "exit_bbo_window_start": exit_window_start,
                "exit_bbo_window_end": exit_window_end,
                "exit_action": "SELL_OPEN_RESTORE_IM_SHORT",
                "exit_window_basis": exit_window_basis,
                "cash_index_1m_outcome": one_outcome,
                "cash_index_3s_observed_outcome": p.outcome,
            }
        )

    events = pd.DataFrame(event_rows)
    quotes = pd.DataFrame(quote_rows)
    events.to_csv(OUT / "event_clock_bridge.csv", index=False)
    quotes.to_csv(OUT / "im_quote_request_manifest.csv", index=False)

    relation_counts = events["grid_relation"].value_counts().to_dict()
    summary = pd.DataFrame(
        [
            {
                "events": int(len(events)),
                "trading_days": int(events["trading_day"].nunique()),
                "entry_exact_3s_price_events": int(events["entry_exact_3s_price_available"].sum()),
                "entry_exact_3s_price_rate": float(events["entry_exact_3s_price_available"].mean()) if len(events) else np.nan,
                "same_outcome_observed": int(relation_counts.get("same_outcome_observed", 0)),
                "timeout_consistent_no_3s_cross": int(relation_counts.get("timeout_consistent_no_3s_cross", 0)),
                "one_minute_extreme_not_observed_3s": int(relation_counts.get("1m_extreme_not_observed_on_3s_points", 0)),
                "directionally_discordant": int(relation_counts.get("directionally_discordant", 0)),
                "narrow_3s_exit_windows": int(quotes["exit_window_basis"].eq("3s_observed_crossing").sum()),
                "timeout_exit_windows": int(quotes["exit_window_basis"].eq("frozen_10m_timeout").sum()),
                "wide_1m_exit_windows": int(quotes["exit_window_basis"].eq("1m_resolution_interval_3s_unobserved").sum()),
            }
        ]
    )
    summary.to_csv(OUT / "summary.csv", index=False)

    request_contract = {
        "schema": "im_hedge_release_quote_request@0.1",
        "account_architecture": "prior_day_IM_short_hedge_release_then_restore",
        "event_policy": "first_frozen_candidate_signal_per_trading_day_only",
        "contract_selection_fields_required_on_prior_trading_day": [
            "contract_code",
            "expiry_date",
            "last_trading_day",
            "daily_volume",
            "daily_open_interest",
            "settlement_price",
        ],
        "suggested_causal_contract_rule_to_freeze_before_replay": (
            "among contracts active on event day and not on their last trading day, "
            "select highest prior-day open interest; tie-break highest prior-day volume; "
            "then nearest expiry"
        ),
        "quote_fields_required_in_manifest_windows": [
            "exchange_timestamp",
            "contract_code",
            "bid_price_1",
            "bid_size_1",
            "ask_price_1",
            "ask_size_1",
            "last_price",
            "cumulative_volume_or_trade_size_if_available",
        ],
        "execution_actions": {
            "entry": "first executable ask: buy-close one historical short",
            "exit": "first executable bid at/after frozen cash-index trigger: sell-open one short",
        },
        "still_required_for_net_replay": [
            "effective-dated exchange fee",
            "broker commission/markup",
            "cash-index/IM basis at entry and exit",
            "slippage/fill rule",
        ],
        "warning": "3s index points narrow trigger clocks only; they are not executable IM quotes",
    }
    (OUT / "im_data_contract.json").write_text(
        json.dumps(request_contract, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print("=== v0.14.2 1m/3s BAR CLOCK ALIGNMENT ===")
    print(align.to_string(index=False))
    print("=== v0.14.2 EXECUTION CLOCK BRIDGE SUMMARY ===")
    print(summary.to_string(index=False))
    print("=== GRID RELATION COUNTS ===")
    print(events["grid_relation"].value_counts(dropna=False).to_string())
    print("=== QUOTE REQUEST MANIFEST PREVIEW ===")
    print(quotes.head(12).to_string(index=False))
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
