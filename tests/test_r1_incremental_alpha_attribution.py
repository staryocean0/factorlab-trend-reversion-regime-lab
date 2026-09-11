import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from research.r1_incremental_alpha_attribution.core import (
    match_events,
    paired_outcomes,
    path_attribution,
    summarize_incremental,
)


def _feature_row(**overrides):
    row = {
        "parent_abs_drift": 0.4,
        "parent_efficiency": 0.3,
        "log1p_parent_age_bars": math.log1p(20),
        "local_vol_30_over_240": 1.1,
    }
    row.update(overrides)
    return row


def test_match_is_exact_on_year_direction_and_clock_bucket_then_nearest():
    events = pd.DataFrame([
        {"cell": "R1_A", "event_day": "2023-05-04", "entry_idx": 100, "parent_direction": 1, "side": "LONG", "clock_bucket": 19, "calendar_year": "2023", "severity": 0.8, **_feature_row()},
    ])
    controls = pd.DataFrame([
        {"cell": "R1_A", "control_day": "2023-03-01", "entry_idx": 10, "parent_direction": 1, "clock_bucket": 19, "calendar_year": "2023", **_feature_row(parent_abs_drift=0.41)},
        {"cell": "R1_A", "control_day": "2023-03-02", "entry_idx": 11, "parent_direction": 1, "clock_bucket": 19, "calendar_year": "2023", **_feature_row(parent_abs_drift=0.80)},
        {"cell": "R1_A", "control_day": "2023-03-03", "entry_idx": 12, "parent_direction": 1, "clock_bucket": 20, "calendar_year": "2023", **_feature_row(parent_abs_drift=0.4001)},
    ])
    matched, meta = match_events(events, controls)
    assert meta["matched_events"] == 1
    assert int(matched.iloc[0].control_entry_idx) == 10
    assert matched.iloc[0].clock_bucket == 19


def test_match_does_not_relax_missing_exact_stratum():
    events = pd.DataFrame([
        {"cell": "R1_B", "event_day": "2024-01-02", "entry_idx": 100, "parent_direction": -1, "side": "SHORT", "clock_bucket": 20, "calendar_year": "2024", "severity": 1.0, **_feature_row()},
    ])
    controls = pd.DataFrame([
        {"cell": "R1_B", "control_day": "2024-01-03", "entry_idx": 20, "parent_direction": -1, "clock_bucket": 19, "calendar_year": "2024", **_feature_row()},
    ])
    matched, meta = match_events(events, controls)
    assert matched.empty
    assert meta["matched_events"] == 0
    assert meta["coverage"] == 0.0


def test_paired_outcomes_are_direction_symmetric():
    prices = np.array([100.0, 101.0, 102.0, 103.0, 104.0, 100.0, 99.0, 98.0, 97.0, 96.0])
    matches = pd.DataFrame([
        {"cell": "R1_A", "event_day": "2023-01-01", "control_day": "2023-01-02", "event_entry_idx": 0, "control_entry_idx": 5, "side": "LONG", "parent_direction": 1, "match_distance": 0.1},
        {"cell": "R1_B", "event_day": "2023-01-01", "control_day": "2023-01-02", "event_entry_idx": 5, "control_entry_idx": 0, "side": "SHORT", "parent_direction": -1, "match_distance": 0.1},
    ])
    out = paired_outcomes(matches, prices, horizons=[1])
    long = out.loc[out.cell.eq("R1_A")].iloc[0]
    short = out.loc[out.cell.eq("R1_B")].iloc[0]
    assert long.event_signed_return > 0
    assert long.control_signed_return < 0
    assert short.event_signed_return > 0
    assert short.control_signed_return < 0


def test_path_segments_and_session_components_are_additive():
    prices = 100.0 * np.exp(np.arange(600) * 0.0001)
    days = np.array(["2023-01-02"] * 300 + ["2023-01-03"] * 300)
    matches = pd.DataFrame([
        {"cell": "R1_A", "event_day": "2023-01-02", "control_day": "2023-01-02", "event_entry_idx": 40, "control_entry_idx": 50, "side": "LONG", "parent_direction": 1, "match_distance": 0.2},
    ])
    path = path_attribution(matches, prices, days).iloc[0]
    event_segments = sum(path[f"event_seg_{a}_{b}_bp"] for a, b in ((0,1),(1,5),(5,15),(15,30),(30,60),(60,120),(120,240)))
    full = math.log(prices[280] / prices[40]) * 10000.0
    assert abs(event_segments - full) < 1e-9
    session_sum = path.event_same_session_bp + path.event_overnight_bp + path.event_next_session_bp
    assert abs(session_sum - full) < 1e-9


def test_incremental_summary_support_flag_uses_all_frozen_conditions():
    rows = []
    for year in range(2021, 2026):
        for side in ("LONG", "SHORT"):
            for k in range(6):
                rows.append({
                    "cell": "R1_A",
                    "event_day": f"{year}-01-{k+1:02d}",
                    "side": side,
                    "horizon": 30,
                    "event_signed_return": 0.002,
                    "control_signed_return": 0.001,
                    "incremental_return": 0.001,
                })
    outcomes = pd.DataFrame(rows)
    meta = {
        "R1_A": {"eligible_events": 60, "matched_events": 60, "coverage": 1.0, "unique_controls": 50, "median_match_distance": 0.2, "p90_match_distance": 0.5},
        "R1_B": {"eligible_events": 1, "matched_events": 0, "coverage": 0.0, "unique_controls": 0, "median_match_distance": None, "p90_match_distance": None},
    }
    summary = summarize_incremental(outcomes, meta, reps=50, seed=1)
    assert summary["R1_A"]["30"]["strong_incremental_support"] is True
    assert summary["R1_A"]["30"]["positive_annual_incremental_mean_years"] == 5
    assert summary["R1_B"]["30"]["strong_incremental_support"] is False


def test_decisive_receipt_preserves_incremental_adjudication():
    repo = Path(__file__).resolve().parents[1]
    path = repo / "docs/ops/evidence/r1_incremental_alpha_20260911/attribution_receipt.json"
    receipt = json.loads(path.read_text(encoding="utf-8"))
    assert receipt["decision"] == "R1_INCREMENTAL_ATTRIBUTION_COMPLETE_NO_HORIZON_SELECTED"
    csi = receipt["incremental_summary"]["000852.SH"]
    star = receipt["incremental_summary"]["000688.SH"]
    assert csi["R1_A"]["15"]["strong_incremental_support"] is True
    assert csi["R1_A"]["30"]["strong_incremental_support"] is True
    assert all(csi["R1_B"][str(h)]["strong_incremental_support"] is False for h in (1, 5, 15, 30, 60, 120, 240))
    assert all(star["R1_B"][str(h)]["strong_incremental_support"] is False for h in (1, 5, 15, 30, 60, 120, 240))
    assert receipt["common_strong_incremental_horizons"] == {"R1_A": [], "R1_B": []}
    assert receipt["horizon_selected"] is False
