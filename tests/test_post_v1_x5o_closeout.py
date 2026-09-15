"""Fail-closed guards for Post-V1 X5O regime-observable identifiability closeout."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"

def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))

def test_x5o_protocol_is_frozen_and_slope_t_independent():
    p = load("TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5O_OBSERVABLE_STATISTICS"
    assert p["reference_calibration_months"] == ["2025-09", "2025-10"]
    assert p["causality"]["all_observables_use_t_minus_1_or_earlier"] is True
    assert p["causality"]["current_t_return_used"] is False
    assert p["causality"]["slope_t_used_in_observables"] is False
    assert p["causality"]["state_label_used_in_observables"] is False
    assert "search_observable_thresholds_on_evaluation_outcomes" in p["forbidden"]

def test_x5o_finds_no_identifiable_regime_observable():
    r = load("TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_RESULT_V1.json")
    assert r["status"] == "X5O_COMPLETE_NO_CAUSAL_REGIME_OBSERVABLE_MEETS_IDENTIFIABILITY_GATES"
    assert r["decision"]["COMMON_REGIME_OBSERVABLE_IDENTIFIED"] is False
    assert r["decision"]["SSE50_CARRIER_REGIME_OBSERVABLE_IDENTIFIED"] is False
    assert r["common_regime_alert"]["spearman_vs_q95_turnover_severity"] < 0.60
    assert r["sse50_carrier_regime_alert"]["spearman_vs_000016_normalized_ratio"] < 0.60
    assert r["sse50_carrier_regime_alert"]["spearman_vs_interaction_loss_severity"] < 0.60
    clue = r["per_observable_descriptive_association"]["CORRELATION_BREAK"]
    assert clue["rho_q95"] > 0.80
    assert clue["first_block_alert_fraction"] < 0.50
    assert r["interpretation"]["new_normalized_strength_law_authorized"] is False

def test_x5o_posthoc_source_agreement_cannot_rescue_gate():
    d = load("TREND_X5O_POSTHOC_OBSERVABLE_SOURCE_AGREEMENT_V1.json")
    assert d["status"] == "POST_HOC_SOURCE_AGREEMENT_DIAGNOSTIC_NOT_USED_FOR_X5O_PRIMARY_DECISION"
    assert d["pearson"] > 0.99999
    assert d["q95_absolute_difference"] < 0.0001
    assert d["used_for_primary_identifiability_decision"] is False
    assert d["threshold_change_authorized"] is False
    assert d["product_adoption_allowed"] is False

def test_post_x5o_decision_keeps_v1_and_x6_frozen():
    u = load("TREND_X4_POST_X5O_UPDATE_V1.json")
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5o_findings"]["common_regime_observable_identified"] is False
    assert u["x5o_findings"]["sse50_carrier_regime_observable_identified"] is False
    assert u["x5o_findings"]["retuning_on_x5o_outcomes_allowed"] is False
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False
