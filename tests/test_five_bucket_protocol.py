"""M4 protocol invariants only; this file computes no market outcomes."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from factor_lab.market_state.trend_regime_baseline import DEFAULT_SIDEWAYS_THRESHOLD
from factor_lab.market_state.trend_regime_profiles import (
    ADMITTED_BAR_INTERVALS,
    trend_regime_profiles,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"


def load_protocol() -> dict:
    return json.loads(PROTOCOL.read_text(encoding="utf-8"))


def test_protocol_identity_and_authority_are_frozen():
    p = load_protocol()
    assert p["schema_id"] == "trend_five_bucket_protocol_m4@1.0"
    assert p["status"] == "FROZEN_BEFORE_M5_OUTCOMES"
    assert p["production_authority"] is False
    assert p["fresh_oos"] is False
    assert p["hypothesis"]["trading_semantics"] is False


def test_t1_t2_and_bucket_boundaries_are_frozen_before_outcomes():
    p = load_protocol()["state_scheme"]
    assert p["t1"] == DEFAULT_SIDEWAYS_THRESHOLD == 2.0
    assert p["primary_t2"] == 4.0
    assert p["sensitivity_t2"] == [3.0, 5.0]
    assert p["buckets"] == {
        "STRONG_DOWN": "s < -T2",
        "DOWN": "-T2 <= s < -T1",
        "SIDEWAYS": "-T1 <= s <= T1",
        "UP": "T1 < s <= T2",
        "STRONG_UP": "s > T2",
    }


def test_primary_and_replication_carriers_cannot_be_pooled():
    carriers = load_protocol()["carriers"]
    assert carriers["primary"] == "000852.SH"
    assert carriers["replication"] == ["000688.SH"]
    assert "never_pool" in carriers["pooling_rule"]


def test_sample_splits_are_chronological_and_holdout_is_not_fresh_oos():
    c = load_protocol()["sample_calendar"]
    dev = c["development"]
    val = c["validation"]
    hold = c["locked_historical_holdout"]
    assert date.fromisoformat(dev["start"]) == date(2020, 7, 23)
    assert date.fromisoformat(dev["end"]) < date.fromisoformat(val["start"])
    assert date.fromisoformat(val["end"]) < date.fromisoformat(hold["start"])
    assert date.fromisoformat(hold["end"]) == date(2025, 12, 31)
    assert c["holdout_label"] == "protocol_holdout_not_fresh_oos"


def test_anchor_profiles_follow_minimum_offset_rule_and_cover_all_intervals():
    p = load_protocol()["profiles"]
    profiles = trend_regime_profiles()
    by_interval = {
        interval: [x for x in profiles if x.bar_interval == interval]
        for interval in ADMITTED_BAR_INTERVALS
    }
    expected_anchors = {
        min(items, key=lambda x: x.session_offset_minutes).profile_id
        for items in by_interval.values()
    }
    assert set(p["anchors"]) == expected_anchors
    assert set(p["anchors"]).isdisjoint(p["phase_sensitivity"])
    assert set(p["anchors"]) | set(p["phase_sensitivity"]) == {
        x.profile_id for x in profiles
    }
    assert p["local_resampling_allowed"] is False
    assert p["substitution_allowed"] is False


def test_horizons_endpoints_and_sample_guards_are_frozen():
    p = load_protocol()
    assert p["forward_horizons_bars"] == [1, 3, 5, 10, 20]
    assert p["primary_horizon_bars"] == 5
    assert p["reversal_horizons_bars"] == [5, 10, 20]
    assert p["primary_reversal_horizon_bars"] == 10
    assert p["metrics"]["primary"]["contrast"] == "strong_minus_moderate_within_direction"
    assert p["metrics"]["primary"]["h1_sign"] == "negative"
    n = p["minimum_sample"]
    assert n["validation_primary_episode_starts_per_group"] == 100
    assert n["holdout_primary_episode_starts_per_group"] == 50
    assert n["secondary_10_20bar_episode_starts_per_group"] == 50


def test_inference_and_holdout_unlock_cannot_be_relaxed_silently():
    p = load_protocol()
    inf = p["inference"]
    assert inf["resampling_unit"] == "ISO_calendar_week_of_episode_start"
    assert inf["bootstrap_replicates"] == 5000
    assert inf["bootstrap_seed"] == 20260914
    assert inf["multiple_testing"].startswith("Holm")
    assert "<= -0.05" in inf["effect_size_guard"]
    assert "only after validation" in p["decision_rules"]["holdout_unlock"]


def test_m4_explicitly_forbids_outcome_computation():
    forbidden = set(load_protocol()["forbidden_in_m4"])
    assert {
        "forward_return_computation",
        "transition_probability_computation",
        "episode_count_by_five_bucket",
        "T2_tuning_from_observed_distribution",
        "reversal_or_excursion_computation",
        "holdout_reading",
    }.issubset(forbidden)
