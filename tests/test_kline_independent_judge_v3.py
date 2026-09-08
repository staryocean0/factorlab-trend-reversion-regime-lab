from __future__ import annotations

import numpy as np
import pandas as pd

from regime_lab.kline_independent_judge_v3 import (
    INDEPENDENT_JUDGE_RADIUS,
    build_independent_judge_frame,
    classify_independent_geometry,
    independent_agreement_grade,
)


def test_independent_geometry_rule_has_four_concrete_states():
    common = dict(median_range_rank=0.5, max_range_rank=0.5)
    assert classify_independent_geometry(
        linear_r=0.9,
        channel_displacement=0.7,
        terminal_channel_location=0.9,
        turning_point_density=0.1,
        **common,
    ) == "UpTrend"
    assert classify_independent_geometry(
        linear_r=-0.9,
        channel_displacement=-0.7,
        terminal_channel_location=0.1,
        turning_point_density=0.1,
        **common,
    ) == "DownTrend"
    assert classify_independent_geometry(
        linear_r=0.1,
        channel_displacement=0.1,
        terminal_channel_location=0.5,
        turning_point_density=0.6,
        **common,
    ) == "Range"
    assert classify_independent_geometry(
        linear_r=0.9,
        channel_displacement=0.7,
        terminal_channel_location=0.9,
        turning_point_density=0.1,
        median_range_rank=0.96,
        max_range_rank=0.5,
    ) == "Shock"


def _synthetic_state_frame(days: int = 24) -> pd.DataFrame:
    parts = []
    base = pd.Timestamp("2025-01-02")
    business_days = pd.bdate_range(base, periods=days)
    cursor = 100.0
    for d, day in enumerate(business_days):
        am = pd.date_range(
            f"{day.date()} 09:30", f"{day.date()} 11:30", freq="5min", tz="Asia/Shanghai"
        )
        pm = pd.date_range(
            f"{day.date()} 13:00", f"{day.date()} 15:00", freq="5min", tz="Asia/Shanghai"
        )
        times = am.append(pm)
        x = np.arange(len(times), dtype=float)
        wave = 0.12 * np.sin((x + d) / 2.0)
        drift = 0.015 * x * (1 if d % 3 != 1 else -1)
        close = cursor + wave + drift
        cursor = float(close[-1] + 0.05)
        parts.append(
            pd.DataFrame(
                {
                    "symbol": "000852.SH",
                    "trading_day": times.strftime("%Y-%m-%d"),
                    "market_time_shanghai": times,
                    "open": close - 0.02,
                    "high": close + 0.08 + 0.01 * (x % 3),
                    "low": close - 0.08 - 0.01 * ((x + 1) % 3),
                    "close": close,
                    "contiguous_run_id": d + 1,
                    "recognition_eligible": True,
                    "online_state": np.where(x % 11 < 6, "UpTrend", "Uncertain"),
                    "oracle_state": "Shock",
                    "signed_efficiency_6": 999.0,
                    "signed_efficiency_12": -999.0,
                    "bdci_12": 999.0,
                    "dii_12": -999.0,
                    "realized_volatility_12": 999.0,
                }
            )
        )
    return pd.concat(parts, ignore_index=True)


def test_independent_judge_does_not_read_recognizer_or_v1_oracle_fields():
    base = _synthetic_state_frame()
    first, _, _ = build_independent_judge_frame(base)
    changed = base.copy()
    changed["online_state"] = "DownTrend"
    changed["oracle_state"] = "Range"
    changed["signed_efficiency_6"] = -12345.0
    changed["signed_efficiency_12"] = 12345.0
    changed["bdci_12"] = -12345.0
    changed["dii_12"] = 12345.0
    changed["realized_volatility_12"] = -12345.0
    second, _, _ = build_independent_judge_frame(changed)
    pd.testing.assert_series_equal(
        first["independent_judge_center_state"],
        second["independent_judge_center_state"],
        check_names=False,
    )


def test_independent_judge_availability_is_exactly_eight_eligible_bars():
    frame, _, _ = build_independent_judge_frame(_synthetic_state_frame())
    eligible = frame.loc[frame["recognition_eligible"]].copy()
    found = False
    for (_, _), group in eligible.groupby(["symbol", "trading_day"], sort=False):
        loc = list(group.index)
        for source_ordinal, source_idx in enumerate(loc[:-INDEPENDENT_JUDGE_RADIUS]):
            if not bool(frame.at[source_idx, "independent_judge_center_eligible"]):
                continue
            target_idx = loc[source_ordinal + INDEPENDENT_JUDGE_RADIUS]
            assert frame.at[target_idx, "independent_judge_available_state"] == frame.at[
                source_idx, "independent_judge_center_state"
            ]
            found = True
            break
        if found:
            break
    assert found


def test_independent_agreement_grade_is_frozen():
    strong_asset = {
        "balanced_accuracy_4state": 0.70,
        "macro_f1_4state": 0.70,
        "transition_f1": 0.55,
        "online_concrete_coverage": 0.90,
    }
    useful_asset = {
        "balanced_accuracy_4state": 0.55,
        "macro_f1_4state": 0.55,
        "transition_f1": 0.35,
        "online_concrete_coverage": 0.80,
    }
    weak_asset = {
        "balanced_accuracy_4state": 0.45,
        "macro_f1_4state": 0.45,
        "transition_f1": 0.20,
        "online_concrete_coverage": 0.80,
    }
    assert independent_agreement_grade({"000852.SH": strong_asset, "000688.SH": strong_asset})["grade"] == "strong_independent_algorithmic_agreement"
    assert independent_agreement_grade({"000852.SH": useful_asset, "000688.SH": useful_asset})["grade"] == "useful_independent_algorithmic_agreement"
    assert independent_agreement_grade({"000852.SH": weak_asset, "000688.SH": strong_asset})["grade"] == "weak_independent_algorithmic_agreement"
