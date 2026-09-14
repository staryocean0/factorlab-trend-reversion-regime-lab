"""Fail-closed regression guards for Post-V1 X5G/X5H closeout."""

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


def test_x5h_protocol_is_frozen_strictly_causal_and_strength_only():
    p = load("TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5H_STATISTICS"
    assert p["research_only"] is True
    assert p["evaluation"]["primary_complete_months"] == ["2026-06", "2026-07", "2026-08"]
    assert p["evaluation"]["common_warmup"] == 320
    assert p["causal_common_scale"]["slow_window"] == 20
    assert p["causal_common_scale"]["fast_window"] == 5
    assert p["causal_common_scale"]["current_target_score_used"] is False
    assert p["causal_common_scale"]["future_information_used"] is False
    assert p["causal_carrier_component"]["slow_window"] == 120
    assert p["causal_carrier_component"]["fast_window"] == 20
    assert set(p["preregistered_candidates"]) == {"X5G_BASE_COMMON20_CARRIER120","ADAPT_CARRIER_BLEND_1P5","ADAPT_COMMON_BLEND_1P5","ADAPT_DUAL_BLEND_1P5","ADAPT_CARRIER_RESET_1P5"}
    assert p["decision_gates"]["stable_research_candidate_requires_all_gates"] is True
    assert p["decision_gates"]["product_adoption_allowed"] is False
    assert p["decision_gates"]["x6_version_bump_allowed"] is False


def test_x5h_primary_candidate_passes_but_remains_research_only():
    r = load("TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_RESULT_V1.json")
    assert r["status"] == "X5H_COMPLETE_PRIMARY_GATE_CANDIDATE_FOUND_MECHANISM_AND_TURNOVER_NOT_RESOLVED"
    assert r["primary_evaluation"]["months"] == ["2026-06", "2026-07", "2026-08"]
    assert r["primary_evaluation"]["measurements_per_carrier"] == 260
    d = r["preregistered_candidates"]["ADAPT_DUAL_BLEND_1P5"]
    assert d["all_gates_pass"] is True
    assert all(d["gates"].values())
    assert d["range_reduction_vs_raw"] > 0.93
    assert d["temporal_reduction_vs_raw"] > 0.20
    assert d["carriers_improved"] == 5
    assert d["interaction_reduction_vs_x5g_base"] > 0.35
    assert r["primary_decision"]["gate_qualified_research_candidate"] == "ADAPT_DUAL_BLEND_1P5"
    assert r["primary_decision"]["product_adoption"] is False
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"


def test_x5h_posthoc_diagnostics_prevent_mechanism_overclaim():
    r = load("TREND_X5H_ADAPTIVE_REGIME_SHIFT_STRENGTH_SCALE_RESULT_V1.json")
    mech = r["post_hoc_mechanism_diagnostic_not_used_for_primary_decision"]
    fast = mech["PURE_FAST_COMMON5_CARRIER20"]
    dual = r["preregistered_candidates"]["ADAPT_DUAL_BLEND_1P5"]
    assert fast["range_reduction_vs_raw"] >= dual["range_reduction_vs_raw"]
    assert fast["temporal_reduction_vs_raw"] >= dual["temporal_reduction_vs_raw"]
    assert fast["carriers_improved"] == 5
    turnover = r["post_hoc_scale_turnover_diagnostic_not_used_for_primary_decision"]
    assert turnover["ADAPT_DUAL_BLEND_1P5"]["median_change_multiple_vs_base"] > 3.0
    assert turnover["ADAPT_DUAL_BLEND_1P5"]["q95_multiple_vs_base"] > 2.0
    decision = r["normalized_strength_decision"]
    assert decision["gate_qualified_research_candidate_exists"] is True
    assert decision["specific_regime_shift_mechanism_identified"] is False
    assert decision["stable_temporal_product_representation_established"] is False
    assert decision["product_strength_semantics_change_supported"] is False
    assert decision["state_boundary_use_supported"] is False


def test_post_x5h_governance_keeps_v1_and_x6_frozen():
    u = load("TREND_X4_POST_X5H_UPDATE_V1.json")
    assert u["status"] == "PRIMARY_RESEARCH_CANDIDATE_FOUND_BUT_MECHANISM_AND_TURNOVER_REQUIRE_PROSPECTIVE_VALIDATION"
    assert u["prior_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5h_primary_result"]["all_preregistered_primary_gates_pass"] is True
    assert u["post_hoc_limits"]["specific_regime_shift_mechanism_identified"] is False
    assert u["representation_status"]["ADAPTIVE_DUAL_BLEND"] == "PROMOTED_TO_PROSPECTIVE_REPLICATION_CANDIDATE_ONLY"
    assert u["representation_status"]["PURE_FAST_5_20"] == "POST_HOC_MECHANISM_COMPARATOR_REQUIRES_PREREGISTRATION"
    assert u["v1_action"] == "NO_CHANGE"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False


def test_handoff_and_roadmap_include_x5h_candidate_and_hold():
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5H" in text
        assert "ADAPT_DUAL_BLEND_1P5" in text
        assert "HOLD" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
    assert "release/trend-regime-v1.0.0" in handoff
    assert "5a563d87d1628379e0d9a04aa7c5500bc30c4bc2" in handoff
