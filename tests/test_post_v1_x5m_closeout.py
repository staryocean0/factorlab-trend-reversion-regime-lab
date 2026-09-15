"""Fail-closed guards for Post-V1 X5M structural validation."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"

def load(name):
    return json.loads((GOV / name).read_text(encoding="utf-8"))

def test_x5m_protocol_freezes_candidate_and_gates_before_statistics():
    p = load("TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5M_CANDIDATE_STATISTICS"
    assert p["frozen_candidate"]["name"] == "ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25"
    assert p["frozen_candidate"]["trigger_abs_log_gap"] == 0.12
    assert p["frozen_candidate"]["partial_fraction"] == 0.50
    assert p["frozen_candidate"]["cooldown_measurements"] == 2
    assert p["frozen_candidate"]["strictly_causal"] is True
    assert p["decision_rule"]["parameter_retuning_allowed"] is False
    assert p["decision_rule"]["gate_relaxation_allowed"] is False
    assert p["governance"]["old_m4_m5_governed_2025_holdout_read_allowed"] is False

def test_x5m_structural_validation_blocks_promotion():
    r = load("TREND_X5M_FROZEN_ANCHORED_STRUCTURAL_VALIDATION_RESULT_V1.json")
    assert r["status"] == "X5M_COMPLETE_FROZEN_ANCHORED_PARTIAL_DOES_NOT_GENERALIZE_ACROSS_STRUCTURAL_BLOCKS"
    assert r["candidate_parameters_changed"] is False
    assert r["gates_changed"] is False
    assert r["structural_block_A"]["passed_gate_count"] == 5
    assert set(r["structural_block_A"]["failed_gates"]) == {"temporal", "q95_turnover"}
    assert r["structural_block_A"]["old_m4_m5_governed_2025_holdout_read"] is False
    assert r["structural_block_B"]["tencent"]["passed_gate_count"] == 6
    assert r["structural_block_B"]["sina"]["passed_gate_count"] == 6
    assert r["structural_block_B"]["tencent"]["interaction_reduction_vs_slow"] < 0
    assert r["structural_block_B"]["sina"]["interaction_reduction_vs_slow"] < 0
    assert r["decision"]["promotion_rule_satisfied"] is False
    assert r["decision"]["stable_structural_generalization_established"] is False
    assert r["decision"]["selected_candidate"] is None
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    for key in ("market_outcomes_computed","trading_return_metrics_computed","strategy_logic_used","runtime_admission_changed","v1_state_boundary_changed","v1_strength_semantics_changed","production_authority","fresh_oos"):
        assert r[key] is False

def test_post_x5m_decision_forbids_retuning_and_keeps_v1_frozen():
    u = load("TREND_X4_POST_X5M_UPDATE_V1.json")
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5m_findings"]["structural_generalization_established"] is False
    assert u["x5m_findings"]["promotion_rule_satisfied"] is False
    assert "NO_RETUNE_ON_X5M_OUTCOMES" in u["representation_status"]["ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25"]
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
