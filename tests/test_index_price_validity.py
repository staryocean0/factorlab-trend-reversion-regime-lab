from __future__ import annotations

import numpy as np
import pandas as pd

from research.index_price_validity.core import evaluate_events, summarize_window


def test_signed_returns_are_symmetric_for_long_and_short():
    prices = np.array([100.0, 100.0, 101.0, 102.0, 99.0])
    days = np.array(["2023-01-01"] * len(prices))
    events = pd.DataFrame(
        [
            {"cell": "R1_A", "family": "R1", "day": "2023-01-01", "confirm_idx": 0, "resolve_idx": 4, "signal_dir": 1, "structural_outcome": "recovery"},
            {"cell": "R1_A", "family": "R1", "day": "2023-01-01", "confirm_idx": 0, "resolve_idx": 4, "signal_dir": -1, "structural_outcome": "failure"},
        ]
    )
    out = evaluate_events(events, prices, days, [1], "TEST")
    assert len(out) == 2
    long_ret = float(out.loc[out.side == "LONG", "signed_return"].iloc[0])
    short_ret = float(out.loc[out.side == "SHORT", "signed_return"].iloc[0])
    assert np.isclose(long_ret, 0.01)
    assert np.isclose(short_ret, -0.01)


def test_mfe_mae_use_signal_direction():
    prices = np.array([100.0, 100.0, 98.0, 95.0, 97.0])
    days = np.array(["2023-01-01"] * len(prices))
    events = pd.DataFrame(
        [{"cell": "R2_A", "family": "R2", "day": "2023-01-01", "confirm_idx": 0, "resolve_idx": 4, "signal_dir": -1, "structural_outcome": "reentry"}]
    )
    out = evaluate_events(events, prices, days, [3], "TEST")
    row = out.iloc[0]
    assert np.isclose(row.signed_return, 0.03)
    assert np.isclose(row.MFE, 0.05)
    assert np.isclose(row.MAE, 0.02)


def test_support_flag_requires_both_sides_and_four_positive_years():
    rows = []
    for year in range(2021, 2026):
        for side, direction in (("LONG", 1), ("SHORT", -1)):
            for i in range(30):
                ret = 0.001 if year != 2025 else (-0.001 if i < 20 else 0.003)
                rows.append(
                    {
                        "symbol": "TEST",
                        "cell": "R1_B",
                        "family": "R1",
                        "event_day": f"{year}-01-02",
                        "entry_day": f"{year}-01-02",
                        "entry_idx": i,
                        "signal_dir": direction,
                        "side": side,
                        "horizon": 60,
                        "signed_return": ret,
                        "MFE": max(ret, 0.002),
                        "MAE": min(ret, -0.001),
                        "structural_outcome": "recovery",
                    }
                )
    frame = pd.DataFrame(rows)
    summary = summarize_window(frame, ["2021", "2022", "2023", "2024", "2025"])
    info = summary["R1_B"]["60"]
    assert info["positive_annual_mean_years"] >= 4
    assert info["support_flags"]["both_LONG_and_SHORT_mean_positive_when_each_side_n_ge_30"] is True
    assert info["robust_price_edge"] is True


def test_missing_side_sample_cannot_be_robust():
    rows = [
        {
            "symbol": "TEST",
            "cell": "R1_A",
            "family": "R1",
            "event_day": "2023-01-02",
            "entry_day": "2023-01-02",
            "entry_idx": i,
            "signal_dir": 1,
            "side": "LONG",
            "horizon": 30,
            "signed_return": 0.001,
            "MFE": 0.002,
            "MAE": -0.001,
            "structural_outcome": "recovery",
        }
        for i in range(40)
    ]
    summary = summarize_window(pd.DataFrame(rows), ["2021", "2022", "2023", "2024", "2025"])
    info = summary["R1_A"]["30"]
    assert info["support_flags"]["both_LONG_and_SHORT_mean_positive_when_each_side_n_ge_30"] is None
    assert info["robust_price_edge"] is False
