"""v0.14.1 execution architecture cost-floor diagnostic.

This is NOT a new signal search. It freezes the v0.13 CSI1000 opening-gap LONG
re-entry candidate and changes only the executable account architecture.

Why first signal per day?
CFFEX close-today fee recognition uses same-day opens before historical
positions. Once an old short hedge is bought closed and then sold open again,
a second buy-close on the same day would first close that new same-day short.
Therefore the clean hedge-release architecture executes at most the first
qualifying event per trading day.

No IM or ETF executable price series is available in the repository. All
vehicle calculations below are deterministic fee/tick floors using the cash
index event level only as a clearly-labelled point-value proxy where needed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from regime_lab.barrier_policy import evaluate_barrier_timeout_policy
from regime_lab.market_data import load_market_data
from regime_lab.reversal_mean_reversion import ReversalFeatureConfig, compute_reversal_features
from regime_lab.robust_mean_reversion import (
    RobustResidualConfig,
    compute_robust_residual_state,
    robust_residual_reentry_signal,
)

OUT = Path("artifacts/reversal_execution_overlay_v0_14_1")
OUT.mkdir(parents=True, exist_ok=True)

SYMBOL = "000852.SH"
START = "2020-07-23"
END = "2025-12-31"
BARRIER_BPS = 10.0
HORIZON_MINUTES = 10

# Public exchange-level constants used only as deterministic cost floors.
CFFEX_NORMAL_FEE_BPS = 0.23
CFFEX_CLOSE_TODAY_FEE_BPS = 2.30
CFFEX_ORDER_FEE_CNY = 1.0
IM_MULTIPLIER = 200.0
IM_TICK_POINTS = 0.2

# SSE ETF competitive trading handling fee: 0.004% each side = 0.4 bps/side.
SSE_ETF_HANDLING_FEE_BPS_PER_SIDE = 0.40
SSE_ETF_TICK_CNY = 0.001


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


def role_for_day(day: pd.Series) -> pd.Series:
    year = pd.to_numeric(day.astype(str).str[:4], errors="coerce")
    return pd.Series(
        np.where(year.eq(2025), "2025_CONFIRMATION", "2020_2024_DEVELOPMENT"),
        index=day.index,
        dtype="string",
    )


def main() -> None:
    raw5 = load_market_data(SYMBOL, "5m", START, END)
    raw1 = load_market_data(SYMBOL, "1m", START, END)
    frame5 = raw5.loc[
        continuous_auction(raw5) & strict_quality_mask(raw5, expected_source_minutes=5)
    ].copy().reset_index(drop=True)
    frame1 = raw1.loc[
        continuous_auction(raw1) & strict_quality_mask(raw1, expected_source_minutes=1)
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
    candidate1 = signal1.eq(1) & h1_mask(frame1) & gap1.lt(0)

    # Execution constraint: at most the first qualifying event per trading day.
    first_idx = (
        frame1.loc[candidate1, ["trading_day", "market_time_shanghai"]]
        .sort_values(["trading_day", "market_time_shanghai"], kind="stable")
        .groupby("trading_day", sort=False)
        .head(1)
        .index
    )
    execution_signal = pd.Series(0, index=frame1.index, dtype="int8")
    execution_signal.loc[first_idx] = 1

    policy = evaluate_barrier_timeout_policy(
        frame1,
        execution_signal,
        barrier_bps=BARRIER_BPS,
        horizon_bars=HORIZON_MINUTES,
    )
    valid = policy["valid"].fillna(False).astype(bool)
    role = role_for_day(frame1["trading_day"])

    events = pd.DataFrame(
        {
            "role": role.loc[valid].astype(str).to_numpy(),
            "market_time_shanghai": frame1.loc[valid, "market_time_shanghai"].astype(str).to_numpy(),
            "trading_day": frame1.loc[valid, "trading_day"].astype(str).to_numpy(),
            "entry_price_cash_index": policy.loc[valid, "entry_price"].to_numpy(dtype=float),
            "outcome": policy.loc[valid, "outcome"].astype(str).to_numpy(),
            "gross_policy_bps": policy.loc[valid, "gross_policy_bps"].to_numpy(dtype=float),
        }
    )
    events["im_one_tick_bps_cash_level_proxy"] = (
        IM_TICK_POINTS / events["entry_price_cash_index"] * 1e4
    )
    events["cffex_two_order_fee_bps_cash_level_proxy"] = (
        (2.0 * CFFEX_ORDER_FEE_CNY)
        / (events["entry_price_cash_index"] * IM_MULTIPLIER)
        * 1e4
    )

    rows = []
    for role_name in ["2020_2024_DEVELOPMENT", "2025_CONFIRMATION"]:
        x = events.loc[events["role"].eq(role_name)].copy()
        gross = float(x["gross_policy_bps"].mean()) if len(x) else np.nan
        tick_proxy = float(x["im_one_tick_bps_cash_level_proxy"].median()) if len(x) else np.nan
        order_proxy = float(x["cffex_two_order_fee_bps_cash_level_proxy"].median()) if len(x) else np.nan

        standalone_fee = CFFEX_NORMAL_FEE_BPS + CFFEX_CLOSE_TODAY_FEE_BPS
        hedge_release_fee = 2.0 * CFFEX_NORMAL_FEE_BPS
        etf_exchange_fee = 2.0 * SSE_ETF_HANDLING_FEE_BPS_PER_SIDE

        etf_residual_before_spread = gross - etf_exchange_fee if len(x) else np.nan
        if np.isfinite(etf_residual_before_spread) and etf_residual_before_spread > 0:
            etf_price_needed_for_one_tick = SSE_ETF_TICK_CNY * 1e4 / etf_residual_before_spread
        else:
            etf_price_needed_for_one_tick = np.inf

        rows.append(
            {
                "role": role_name,
                "raw_candidate_events_before_first_per_day": int(
                    candidate5.loc[
                        (frame5["market_time_shanghai"].dt.year.eq(2025) if role_name == "2025_CONFIRMATION" else frame5["market_time_shanghai"].dt.year.le(2024))
                    ].sum()
                ),
                "first_signal_per_day_events": int(len(x)),
                "target_first": int(x["outcome"].eq("target_first").sum()),
                "stop_first": int(x["outcome"].eq("stop_first").sum()),
                "time_out": int(x["outcome"].eq("time_out").sum()),
                "gross_policy_mean_bps": gross,
                "standalone_im_exchange_trade_fee_bps": standalone_fee,
                "standalone_im_residual_before_other_friction_bps": gross - standalone_fee,
                "hedge_release_im_exchange_trade_fee_bps": hedge_release_fee,
                "hedge_release_im_residual_before_spread_basis_broker_bps": gross - hedge_release_fee,
                "median_im_one_tick_bps_cash_level_proxy": tick_proxy,
                "median_cffex_two_order_fee_bps_cash_level_proxy": order_proxy,
                "hedge_release_residual_after_exchange_plus_1tick_plus_order_proxy_bps": (
                    gross - hedge_release_fee - tick_proxy - order_proxy
                ),
                "sse_etf_exchange_handling_fee_round_trip_bps": etf_exchange_fee,
                "etf_residual_before_spread_commission_bps": etf_residual_before_spread,
                "etf_price_required_for_one_tick_spread_to_fit_residual_cny": etf_price_needed_for_one_tick,
            }
        )

    summary = pd.DataFrame(rows)
    events.to_csv(OUT / "events_first_signal_per_day.csv", index=False)
    summary.to_csv(OUT / "execution_cost_floor_summary.csv", index=False)

    print("=== v0.14.1 FIRST-SIGNAL-PER-DAY EXECUTION COST FLOOR ===")
    print(summary.to_string(index=False))
    print("NOTES")
    print("- standalone IM = flat -> buy open -> same-day sell close: close-today fee applies")
    print("- hedge release = existing prior-day IM short -> buy close old short -> later sell open")
    print("- IM tick/order bps use cash-index entry level only as a proxy; executable IM data still required")
    print("- ETF price threshold is the minimum unit price for a one-tick marketable spread to fit after SSE handling fee, before broker commission")
    print("RESULT_DIR", OUT)


if __name__ == "__main__":
    main()
