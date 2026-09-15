"""Fail-closed regression guards for Post-V1 X5G/X5H/X5I/X5J closeout."""

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


def test_x5i_protocol_source_recovery_and_erratum_are_fail_closed():
    p = load("TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_PROTOCOL_V1.json")
    block = load("TREND_X5I_EASTMONEY_SOURCE_BLOCK_RECEIPT_V1.json")
    recovery = load("TREND_X5I_SOURCE_RECOVERY_PROTOCOL_V1.json")
    depth = load("TREND_X5I_TENCENT_DEPTH_EXTENSION_RECEIPT_V1.json")
    err = load("TREND_X5I_PROTOCOL_ERRATUM_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5I_SOURCE_ACQUISITION_AND_STATISTICS"
    assert p["preregistered_gates"]["turnover_median_noninferiority_gate"].endswith("<= 2.0")
    assert p["preregistered_gates"]["turnover_q95_noninferiority_gate"].endswith("<= 2.0")
    assert block["status"] == "X5I_PRIMARY_SOURCE_BLOCKED_NO_CANDIDATE_DECISION"
    assert block["data_absence_proven"] is False
    assert block["candidate_statistics_computed"] is False
    assert recovery["status"] == "FROZEN_AFTER_PRIMARY_SOURCE_BLOCK_BEFORE_ALTERNATE_SOURCE_STATISTICS"
    assert recovery["candidate_redefinition_allowed"] is False
    assert recovery["gate_redefinition_allowed"] is False
    assert depth["request_depth"] == 800
    assert depth["filtered_rows_per_carrier"] == 680
    assert depth["public_2025_rows_used_for_candidate_statistics"] is False
    assert depth["old_m4_m5_governed_2025_holdout_read"] is False
    assert err["status"] == "SEALED_BEFORE_X5I_CANDIDATE_STATISTICS"
    assert err["x5i_candidate_statistics_computed_before_erratum"] is False
    assert err["candidate_parameters_changed_from_x5h"] is False


def test_x5i_independent_source_replication_fails_turnover_aware_selection():
    r = load("TREND_X5I_PROSPECTIVE_FAST_VS_ADAPTIVE_STRENGTH_SCALE_RESULT_V1.json")
    assert r["status"] == "X5I_COMPLETE_INDEPENDENT_SOURCE_REPLICATION_TURNOVER_GATE_REJECTS_FAST_AND_ADAPTIVE"
    assert r["provider"] == "Tencent public native 60m index kline"
    assert r["aligned_measurements_per_carrier"] == 661
    assert r["primary_evaluation"] == {"months": ["2026-06", "2026-07", "2026-08"], "measurements_per_carrier": 260}
    slow = r["candidates"]["SLOW_COMMON20_CARRIER120"]
    fast = r["candidates"]["FAST_COMMON5_CARRIER20"]
    dual = r["candidates"]["ADAPT_DUAL_BLEND_1P5"]
    assert slow["gates"]["turnover_median"] is True and slow["gates"]["turnover_q95"] is True
    assert slow["gates"]["temporal"] is False and slow["gates"]["breadth"] is False
    assert fast["range_reduction_vs_raw"] > 0.93 and fast["temporal_ratio_reduction_vs_raw"] > 0.23
    assert fast["carriers_with_lower_monthly_ratio_than_raw"] == 5
    assert fast["turnover_median_multiple_vs_slow"] > 3.0
    assert fast["turnover_q95_multiple_vs_slow"] > 2.0
    assert fast["gates"]["turnover_median"] is False and fast["gates"]["turnover_q95"] is False
    assert dual["range_reduction_vs_raw"] > 0.93 and dual["temporal_ratio_reduction_vs_raw"] > 0.22
    assert dual["carriers_with_lower_monthly_ratio_than_raw"] == 5
    assert dual["turnover_median_multiple_vs_slow"] > 3.0
    assert dual["turnover_q95_multiple_vs_slow"] > 2.0
    assert dual["gates"]["turnover_median"] is False and dual["gates"]["turnover_q95"] is False
    assert r["primary_decision"]["all_gate_qualified_candidates"] == []
    assert r["primary_decision"]["selected_candidate"] is None
    assert r["primary_decision"]["short_memory_scale_benefit_replicated_on_independent_source"] is True
    assert r["primary_decision"]["turnover_concern_replicated_prospectively"] is True
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    assert r["fresh_oos"] is False


def test_post_x5i_decision_and_handoff_keep_v1_frozen():
    u = load("TREND_X4_POST_X5I_UPDATE_V1.json")
    assert u["status"] == "INDEPENDENT_SOURCE_REPLICATION_CONFIRMS_SHORT_MEMORY_BENEFIT_BUT_TURNOVER_BLOCKS_ADOPTION"
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["candidate_status"]["FAST_COMMON5_CARRIER20"].endswith("TURNOVER_NONINFERIORITY_FAIL")
    assert u["candidate_status"]["ADAPT_DUAL_BLEND_1P5"].endswith("TURNOVER_NONINFERIORITY_FAIL")
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5I" in text
        assert "FAST_COMMON5_CARRIER20" in text
        assert "ADAPT_DUAL_BLEND_1P5" in text
        assert "HOLD" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text


def test_x5j_protocol_freezes_small_candidate_set_and_turnover_gates():
    p = load("TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5J_CANDIDATE_STATISTICS"
    assert p["research_only"] is True
    assert p["development_source"]["primary_complete_months"] == ["2026-06", "2026-07", "2026-08"]
    assert p["cross_provider_replication_source"]["provider"] == "Sina public native 60m index kline"
    assert set(p["turnover_regularized_candidates"]) == {"FAST_CAP_0P06", "FAST_EWMA_A0P35", "DUAL_CAP_0P06"}
    assert p["decision_gates"]["turnover_median_multiple_vs_slow_max"] == 2.0
    assert p["decision_gates"]["turnover_q95_multiple_vs_slow_max"] == 2.0
    assert p["selection_rule"]["product_adoption_allowed"] is False
    assert p["selection_rule"]["x6_version_bump_allowed"] is False
    assert p["fresh_oos"] is False


def test_x5j_finds_no_gate_qualified_regularized_candidate_on_either_provider():
    r = load("TREND_X5J_TURNOVER_REGULARIZED_STRENGTH_SCALE_RESULT_V1.json")
    assert r["status"] == "X5J_COMPLETE_NO_CANDIDATE_PASSES_STABILITY_AND_TURNOVER_GATES"
    assert r["tencent"]["qualified_candidates"] == []
    assert r["sina_replication"]["qualified_candidates"] == []
    assert r["cross_provider_qualified_candidates"] == []
    assert r["selected_candidate_by_preregistered_rule"] is None
    cap = r["tencent"]["candidates"]["FAST_CAP_0P06"]
    ewma = r["tencent"]["candidates"]["FAST_EWMA_A0P35"]
    dualcap = r["tencent"]["candidates"]["DUAL_CAP_0P06"]
    assert cap["turnover_median_multiple_vs_slow"] < 2.0
    assert cap["temporal_reduction_vs_raw"] < 0.0
    assert cap["carriers_improved"] == 2
    assert ewma["temporal_reduction_vs_raw"] > 0.25
    assert ewma["carriers_improved"] == 4
    assert ewma["turnover_q95_multiple_vs_slow"] < 2.0
    assert ewma["turnover_median_multiple_vs_slow"] > 3.0
    assert dualcap["turnover_median_multiple_vs_slow"] < 2.0
    assert dualcap["temporal_reduction_vs_raw"] <= 0.0
    assert r["normalized_strength_decision"]["simple_cap_solution_supported"] is False
    assert r["normalized_strength_decision"]["simple_ewma_solution_supported"] is False
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    assert r["fresh_oos"] is False


def test_x5j_posthoc_diagnostic_explains_continuous_update_failure_modes():
    d = load("TREND_X5J_POSTHOC_UPDATE_FREQUENCY_DIAGNOSTIC_V1.json")
    assert d["status"] == "POST_HOC_MECHANISM_DIAGNOSTIC_NOT_USED_FOR_X5J_PRIMARY_DECISION"
    cap = d["metrics"]["FAST_CAP_0P06"]
    for key in ("q10", "q25", "q50", "q75", "q90", "q95"):
        assert cap[key] == 0.06
    ewma = d["metrics"]["FAST_EWMA_A0P35"]
    fast = d["metrics"]["FAST_COMMON5_CARRIER20"]
    assert ewma["q95"] < fast["q95"]
    assert ewma["q50"] > d["metrics"]["SLOW_COMMON20_CARRIER120"]["q50"]
    assert d["used_for_primary_candidate_selection"] is False
    assert d["product_adoption_allowed"] is False


def test_post_x5j_decision_and_handoff_keep_v1_and_x6_frozen():
    u = load("TREND_X4_POST_X5J_UPDATE_V1.json")
    assert u["status"] == "X5J_NO_GATE_QUALIFIED_TURNOVER_REGULARIZED_CANDIDATE"
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5j_findings"]["tencent_and_sina_behavior_consistent"] is True
    assert u["x5j_findings"]["cross_provider_gate_qualified_candidate_exists"] is False
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5J" in text
        assert "FAST_EWMA_A0P35" in text
        assert "HOLD" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
