"""Fail-closed regression guards for Post-V1 X5H closeout."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


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
    assert set(p["preregistered_candidates"]) == {
        "X5G_BASE_COMMON20_CARRIER120",
        "ADAPT_CARRIER_BLEND_1P5",
        "ADAPT_COMMON_BLEND_1P5",
        "ADAPT_DUAL_BLEND_1P5",
        "ADAPT_CARRIER_RESET_1P5",
    }
    assert p["decision_gates"]["stable_research_candidate_requires_all_gates"] is True
    assert p["decision_gates"]["product_adoption_allowed"] is False
    assert p["decision_gates"]["x6_version_bump_allowed"] is False
    assert p["production_authority"] is False
    assert p["fresh_oos"] is False


def test_x5h_primary_candidate_passes_research_gates_but_is_not_adopted():
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
    assert "does not identify" in mech["finding"]
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


def test_x5h_handoff_mentions_candidate_and_hold():
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5H" in text
        assert "ADAPT_DUAL_BLEND_1P5" in text
        assert "PURE_FAST" in text or "pure-fast" in text
        assert "HOLD" in text
        assert "NO V1 CHANGE" in text or "V1" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
    assert "release/trend-regime-v1.0.0" in handoff
    assert "5a563d87d1628379e0d9a04aa7c5500bc30c4bc2" in handoff
