"""Fail-closed guards for Post-V1 X5L partial-reset/cooldown closeout."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def test_x5l_protocol_is_frozen_strength_only_and_no_grid_search():
    p = load("TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5L_CANDIDATE_STATISTICS"
    assert p["research_only"] is True
    assert p["targets"]["strictly_causal"] is True
    assert p["targets"]["current_t_used_for_target_scale"] is False
    assert p["targets"]["future_information_allowed"] is False
    assert set(p["preregistered_candidates"]) == {
        "SLOW_COMMON20_CARRIER120",
        "FAST_COMMON5_CARRIER20",
        "PARTIAL_PERSIST2_GAP0P10_F0P50_COOLDOWN2",
        "PARTIAL_DEADBAND0P12_F0P50_COOLDOWN2",
        "ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25",
    }
    assert p["preregistered_gates"]["interaction_reduction_vs_slow"] == ">= 0.20"
    assert p["preregistered_gates"]["update_fraction"] == "<= 0.35"
    assert "parameter_grid_search_on_X5L_outcomes" in p["forbidden"]


def test_x5l_has_cross_provider_near_gate_candidate_but_no_selection():
    r = load("TREND_X5L_PARTIAL_RESET_COOLDOWN_STRENGTH_SCALE_RESULT_V1.json")
    assert r["status"] == "X5L_COMPLETE_NO_GATE_QUALIFIED_CANDIDATE_ANCHORED_PARTIAL_PASSES_6_OF_7_GATES"
    assert r["tencent"]["qualified_candidates"] == []
    assert r["sina_replication"]["qualified_candidates"] == []
    assert r["cross_provider_qualified_candidates"] == []
    assert r["selected_candidate_by_preregistered_rule"] is None
    a = r["tencent"]["candidates"]["ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25"]
    assert a["passed_gate_count"] == 6 and a["total_gate_count"] == 7
    assert a["failed_gates"] == ["interaction"]
    assert a["mean_turnover_multiple_vs_slow"] < 2.0
    assert a["q95_turnover_multiple_vs_slow"] < 2.0
    assert a["update_fraction"] < 0.35
    assert 0.18 < a["interaction_reduction_vs_slow"] < 0.20
    assert r["normalized_strength_decision"]["gate_qualified_candidate_exists"] is False
    assert r["normalized_strength_decision"]["cross_provider_near_gate_candidate_exists"] is True
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    assert r["fresh_oos"] is False


def test_x5l_posthoc_diagnostic_cannot_relax_gate_or_retune():
    d = load("TREND_X5L_POSTHOC_INTERACTION_DIAGNOSTIC_V1.json")
    assert d["status"] == "POST_HOC_MECHANISM_DIAGNOSTIC_NOT_USED_FOR_X5L_PRIMARY_DECISION"
    assert d["tencent"]["anchored_monthly_cell_max_to_min"] > d["tencent"]["required_for_20pct_interaction_gate"]
    assert d["sina"]["anchored_monthly_cell_max_to_min"] > d["sina"]["required_for_20pct_interaction_gate"]
    assert d["tencent"]["max_cell"]["carrier"] == "000688.SH"
    assert d["tencent"]["min_cell"]["carrier"] == "000300.SH"
    assert d["used_for_primary_candidate_selection"] is False
    assert d["parameter_change_authorized"] is False
    assert d["product_adoption_allowed"] is False


def test_post_x5l_decision_keeps_v1_and_x6_frozen():
    u = load("TREND_X4_POST_X5L_UPDATE_V1.json")
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5l_findings"]["anchored_partial_candidate_passes_six_of_seven_gates_on_both_providers"] is True
    assert u["x5l_findings"]["only_failed_gate"] == "interaction"
    assert u["x5l_findings"]["retuning_on_x5l_outcomes_allowed"] is False
    assert u["v1_action"] == "NO_CHANGE"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False
