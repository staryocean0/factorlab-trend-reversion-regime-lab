"""Fail-closed guards for Post-V1 X5N structural failure attribution and X5O regime-observable identifiability."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def test_x5n_protocol_freezes_attribution_without_retuning():
    p = load("TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_PROTOCOL_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5N_ATTRIBUTION_STATISTICS"
    assert p["frozen_subject"] == "ANCHORED_PARTIAL_DB0P12_F0P50_COOLDOWN2_SLOW25"
    assert p["subject_parameters_changed"] is False
    assert p["x5m_gates_changed"] is False
    assert set(p["attribution_hypotheses"]) == {
        "CARRIER_COMPOSITION",
        "MARKET_REGIME_CONDITIONALITY",
        "COMMON_SCALE_ESTIMATOR",
        "CLOCK_STRUCTURE",
    }
    assert "retune_anchor_weight" in p["forbidden"]
    assert "promote_any_counterfactual_estimator" in p["forbidden"]


def test_x5n_result_supports_regime_conditionality_not_local_parameter_fix():
    r = load("TREND_X5N_STRUCTURAL_FAILURE_ATTRIBUTION_RESULT_V1.json")
    assert r["status"] == "X5N_COMPLETE_REGIME_CONDITIONALITY_SUPPORTED_SINGLE_UNIFIED_STATEFUL_LAW_NOT_ESTABLISHED"
    assert r["subject_parameters_changed"] is False
    early = r["early_block_attribution"]
    assert all(v > 2.0 for v in early["q95_turnover_multiple_by_carrier"].values())
    b = r["block_b_000016_attribution"]
    assert b["temporal_improvement_000016"] < 0
    assert all(v > 0 for v in b["other_carrier_temporal_improvements"].values())
    assert r["carrier_composition_panel"]["strong_composition_attribution"] is False
    assert r["common_estimator_panel"]["strong_estimator_attribution"] is False
    assert r["clock_panel"]["conclusion"] == "CLOCK_STRUCTURE_NOT_IDENTIFIABLE_FOR_PRIMARY_FAILURE"
    a = r["attribution_summary"]
    assert a["market_regime_conditionality"] == "SUPPORTED"
    assert a["carrier_specific_regime_interaction_for_000016"] == "SUPPORTED"
    assert a["single_unified_stateful_normalization_law"] == "NOT_ESTABLISHED"
    assert r["decision"]["retune_on_x5n_outcomes_allowed"] is False
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    assert r["fresh_oos"] is False


def test_post_x5n_decision_and_docs_keep_product_boundary_frozen():
    u = load("TREND_X4_POST_X5N_UPDATE_V1.json")
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5n_findings"]["retuning_on_x5n_outcomes_allowed"] is False
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_state_boundary_changed"] is False
    assert u["v1_strength_semantics_changed"] is False
    for path in (ROOT / "CONTINUE_HERE.md", ROOT / "docs" / "ROADMAP.md"):
        text = path.read_text(encoding="utf-8")
        assert "X5N" in text
        assert "MARKET_REGIME_CONDITIONALITY" in text
        assert "CLOCK_STRUCTURE" in text
        assert "RETUNE_ON_X5N_OUTCOMES" in text
        assert "X6" in text and "HOLD" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text


def test_x5o_no_preregistered_causal_observable_is_identified():
    p = load("TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_PROTOCOL_V1.json")
    r = load("TREND_X5O_CAUSAL_REGIME_OBSERVABLE_IDENTIFIABILITY_RESULT_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5O_OBSERVABLE_STATISTICS"
    assert p["causality"]["slope_t_used_in_observables"] is False
    assert p["causality"]["current_t_return_used"] is False
    assert r["status"] == "X5O_COMPLETE_NO_CAUSAL_REGIME_OBSERVABLE_MEETS_IDENTIFIABILITY_GATES"
    assert r["decision"]["COMMON_REGIME_OBSERVABLE_IDENTIFIED"] is False
    assert r["decision"]["SSE50_CARRIER_REGIME_OBSERVABLE_IDENTIFIED"] is False
    assert r["common_regime_alert"]["spearman_vs_q95_turnover_severity"] < 0.60
    assert r["sse50_carrier_regime_alert"]["spearman_vs_000016_normalized_ratio"] < 0.60
    clue = r["per_observable_descriptive_association"]["CORRELATION_BREAK"]
    assert clue["rho_q95"] > 0.80
    assert clue["first_block_alert_fraction"] < 0.50
    assert r["interpretation"]["new_normalized_strength_law_authorized"] is False


def test_x5o_posthoc_source_agreement_does_not_change_decision():
    d = load("TREND_X5O_POSTHOC_OBSERVABLE_SOURCE_AGREEMENT_V1.json")
    u = load("TREND_X4_POST_X5O_UPDATE_V1.json")
    assert d["status"] == "POST_HOC_SOURCE_AGREEMENT_DIAGNOSTIC_NOT_USED_FOR_X5O_PRIMARY_DECISION"
    assert d["pearson"] > 0.99999
    assert d["q95_absolute_difference"] < 0.0001
    assert d["threshold_change_authorized"] is False
    assert u["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["x5o_findings"]["common_regime_observable_identified"] is False
    assert u["x5o_findings"]["sse50_carrier_regime_observable_identified"] is False
    assert u["x5o_findings"]["retuning_on_x5o_outcomes_allowed"] is False
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False
