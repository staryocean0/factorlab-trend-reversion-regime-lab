"""Fail-closed regression guards for Post-V1 X5G closeout."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def test_x5g_protocol_is_strength_only_strictly_causal_and_preregistered():
    p = load("TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5G_STATISTICS"
    assert p["frozen_measurement"]["lookback_bars"] == 20
    assert p["frozen_measurement"]["v1_state_boundary_t1"] == 2.0
    assert p["causal_decomposition"]["current_t_used_to_estimate_own_scale"] is False
    assert p["causal_decomposition"]["future_information_allowed"] is False
    assert p["fair_evaluation"]["common_warmup_measurements"] == 320
    assert [(x["common_window"], x["carrier_window"]) for x in p["candidates"]] == [(20,120),(40,120),(40,240),(80,240)]
    assert p["decision_constraints"]["state_boundary_change_allowed"] is False
    assert p["decision_constraints"]["strength_semantics_change_allowed"] is False


def test_x5g_improves_cross_carrier_alignment_but_establishes_no_stable_representation():
    r = load("TREND_X5G_DYNAMIC_COMMON_SCALE_CARRIER_INTERACTION_RESULT_V1.json")
    assert r["status"] == "X5G_COMPLETE_CROSS_CARRIER_ALIGNMENT_IMPROVED_STABLE_TEMPORAL_REPRESENTATION_NOT_ESTABLISHED"
    assert r["aligned_measurements_per_carrier"] == 661
    assert r["common_evaluation"]["measurements_per_carrier"] == 341
    assert r["causal_identity"]["future_information_used"] is False
    assert r["causal_identity"]["common_factor_for_each_carrier_uses_other_four_carriers_only"] is True
    assert r["primary_decision"]["all_candidates_pass_cross_carrier_scale_gate"] is True
    assert r["primary_decision"]["any_candidate_passes_all_stability_gates"] is False
    assert r["primary_decision"]["stable_normalized_strength_representation_established"] is False
    c20 = r["candidates"]["COMMON20_CARRIER120"]
    assert c20["range_reduction_vs_raw"] > 0.80
    assert c20["temporal_ratio_reduction_vs_raw"] > 0.35
    assert c20["carriers_with_lower_monthly_ratio_than_raw"] == 4
    assert c20["gates"]["interaction"] is False
    assert c20["monthly_cell_max_to_min"] > 2.4080
    for c in r["candidates"].values():
        assert c["all_stability_gates_pass"] is False
    assert r["normalized_strength_decision"]["cross_carrier_dynamic_diagnostic_supported"] is True
    assert r["normalized_strength_decision"]["stable_temporal_representation_established"] is False
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    for key in ("market_outcomes_computed", "trading_return_metrics_computed", "strategy_logic_used", "old_m4_m5_2025_holdout_read", "runtime_admission_changed", "v1_state_boundary_changed", "v1_strength_semantics_changed", "production_authority", "fresh_oos"):
        assert r[key] is False


def test_post_x5g_decision_keeps_x6_hold_and_v1_unchanged():
    u = load("TREND_X4_POST_X5G_UPDATE_V1.json")
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["calibration_family_status"]["DYNAMIC_COMMON_PLUS_SLOW_CARRIER_NORMALIZATION"] == "CROSS_CARRIER_ALIGNMENT_SUPPORTED_TEMPORAL_STABILITY_NOT_ESTABLISHED"
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_parameter_changed"] is False
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False


def test_handoff_and_roadmap_include_x5g_closeout():
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5G" in text
        assert "HOLD" in text
        assert "NO CHANGE" in text or "NO_CHANGE" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
