from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from regime_lab.state_frequency_inference import (
    cost_survival_summary,
    day_block_break_even_uncertainty,
    frequency_contrasts,
    seasonality_matched_summary,
)


def _observations() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    days = pd.date_range("2025-01-02", periods=20, freq="B")
    for day_index, day in enumerate(days):
        trading_day = day.strftime("%Y-%m-%d")
        for horizon in (1, 2, 3, 5, 10, 15, 30):
            for state, base in (("Unsafe", 2.0), ("Recovering", 0.5)):
                for bucket in (1, 2):
                    rows.append(
                        {
                            "symbol": "000852.SH",
                            "trading_day": trading_day,
                            "session_segment": "AM",
                            "clock_bucket_15m": bucket,
                            "state": state,
                            "family": "trend",
                            "horizon_minutes": horizon,
                            "gross_edge_bp": base + 0.01 * horizon + 0.001 * day_index,
                            "turnover_units": 1.0,
                        }
                    )
    return pd.DataFrame(rows)


def test_seasonality_matching_excludes_one_state_strata_and_equalizes_mass():
    obs = _observations()
    one_state = obs.iloc[[0]].copy()
    one_state["clock_bucket_15m"] = 99
    obs = pd.concat([obs, one_state], ignore_index=True)

    matched = seasonality_matched_summary(obs)
    unsafe = matched.loc[
        matched["state"].eq("Unsafe")
        & matched["family"].eq("trend")
        & matched["horizon_minutes"].eq(1)
    ].iloc[0]
    recovering = matched.loc[
        matched["state"].eq("Recovering")
        & matched["family"].eq("trend")
        & matched["horizon_minutes"].eq(1)
    ].iloc[0]

    assert unsafe["matched_effective_weight"] == pytest.approx(
        recovering["matched_effective_weight"]
    )
    assert unsafe["matched_strata"] == recovering["matched_strata"]
    assert unsafe["matched_strata"] == 2


def test_frequency_contrast_is_unsafe_minus_recovering():
    curve = seasonality_matched_summary(_observations())
    contrast = frequency_contrasts(curve)
    row = contrast.loc[contrast["horizon_minutes"].eq(5)].iloc[0]
    assert row["delta_break_even_bp"] == pytest.approx(row["Unsafe"] - row["Recovering"])
    assert row["delta_break_even_bp"] > 0


def test_cost_survival_uses_fixed_short_and_long_sets():
    curve = seasonality_matched_summary(_observations())
    survival = cost_survival_summary(curve)
    row = survival.loc[
        survival["state"].eq("Unsafe")
        & survival["family"].eq("trend")
        & survival["oneway_cost_bp"].eq(1.0)
    ].iloc[0]
    assert row["available_short_horizons"] == 4
    assert row["available_long_horizons"] == 3
    assert row["positive_short_horizons"] == 4


def test_day_block_uncertainty_is_deterministic_and_holm_adjusted():
    obs = _observations()
    first = day_block_break_even_uncertainty(obs, n_boot=300, seed=17)
    second = day_block_break_even_uncertainty(obs, n_boot=300, seed=17)
    pd.testing.assert_frame_equal(first, second)
    assert len(first) == 7
    assert set(first["horizon_minutes"]) == {1, 2, 3, 5, 10, 15, 30}
    assert (first["delta_break_even_bp"] > 0).all()
    assert (first["p_holm_7"] >= first["p_raw"]).all()
    assert np.isfinite(first["bootstrap_se_bp"]).all()


def test_bootstrap_rejects_too_few_replicates():
    with pytest.raises(ValueError, match="at least 200"):
        day_block_break_even_uncertainty(_observations(), n_boot=199)
