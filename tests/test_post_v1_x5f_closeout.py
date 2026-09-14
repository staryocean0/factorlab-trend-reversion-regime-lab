"""Fail-closed regression guards for Post-V1 X5F strength decomposition."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def test_x5f_protocol_freezes_strength_only_decomposition_and_v1_boundary():
    p = load("TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_PROTOCOL_V1.json")
    m = load("TREND_X5F_DECOMPOSITION_METHOD_V1.json")
    assert p["status"] == "FROZEN_BEFORE_X5F_DECOMPOSITION_STATISTICS"
    assert p["frozen_measurement"]["lookback_bars"] == 20
    assert p["frozen_measurement"]["v1_state_boundary_t1"] == 2.0
    assert p["frozen_measurement"]["v1_state_boundary_must_not_change"] is True
    assert p["primary_decomposition"]["state_boundary_use"] == "forbidden"
    assert p["decision_rule"]["product_adoption_allowed"] is False
    assert p["decision_rule"]["x6_version_bump_allowed"] is False
    assert m["status"] == "FROZEN_BEFORE_X5F_DECOMPOSITION_STATISTICS"
    assert m["out_of_time_split"]["training_months"] == ["2026-01", "2026-02", "2026-03", "2026-04"]
    assert m["out_of_time_split"]["evaluation_months"] == ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09"]
    assert m["leave_one_carrier_out"]["future_heldout_information_forbidden"] is True


def test_x5f_clock_source_identifiability_remains_fail_closed():
    r = load("TREND_X5F_CLOCK_SOURCE_IDENTIFIABILITY_RECEIPT_V1.json")
    assert r["status"] == "IDENTIFIABILITY_AUDIT_COMPLETE_BEFORE_X5F_DECOMPOSITION_STATISTICS"
    assert r["alternate_assets"]["STAR50_DataHub_60m_offset30"]["overlaps_primary_2026_window"] is True
    assert r["alternate_assets"]["STAR50_DataHub_60m_offset45"]["overlaps_primary_2026_window"] is True
    assert r["alternate_assets"]["CSI1000_DataHub_60m_offset30"]["overlaps_primary_2026_window"] is False
    assert r["identifiable_components"]["STAR50_same_provider_clock_phase_effect"]["label"] == "clock_phase_effect"
    assert r["identifiable_components"]["STAR50_sina_vs_datahub"]["label"] == "confounded_source_clock"
    assert "pure_provider_effect_at_identical_60m_clock_in_2026" in r["not_identified"]
    assert r["old_m4_m5_2025_holdout_read"] is False


def test_x5f_decomposition_supports_diagnostic_but_not_stable_product_representation():
    r = load("TREND_X5F_60M_STRENGTH_SCALE_DECOMPOSITION_RESULT_V1.json")
    assert r["status"] == "X5F_COMPLETE_CARRIER_AND_COMMON_TIME_EFFECTS_IDENTIFIED_STABLE_NORMALIZED_STRENGTH_NOT_ESTABLISHED"
    v = r["decomposition"]["descriptive_balanced_anova_log_cell_variance_fractions"]
    assert 0.20 < v["carrier"] < 0.40
    assert 0.20 < v["common_time"] < 0.40
    assert v["residual"] > 0.35
    assert abs(v["carrier"] + v["common_time"] + v["residual"] - 1.0) < 0.001
    loo = r["leave_one_carrier_out"]
    assert loo["future_heldout_information_used_for_factor_estimation"] is False
    assert loo["range_reduction_fraction"] > 0.75
    assert loo["normalized_heldout_carrier_median_max_to_min"] < loo["raw_May_Sep_carrier_median_max_to_min"]
    assert max(loo["heldout_monthly_normalized_strength_max_to_min"].values()) > 2.0
    oot = r["out_of_time_carrier_factor_stability"]
    assert oot["spearman_rank_correlation"] < 1.0
    assert oot["max_multiplicative_factor_change"] > 1.20
    assert r["decomposition"]["residual_cell_factor_max_to_min"] > 2.0
    decision = r["normalized_strength_decision"]
    assert decision["cross_carrier_diagnostic_supported"] is True
    assert decision["stable_temporal_representation_established"] is False
    assert decision["state_boundary_use_supported"] is False
    assert decision["product_strength_semantics_change_supported"] is False
    assert r["v1_action"] == "NO_CHANGE"
    assert r["x6_readiness"] == "HOLD_NOT_READY"
    for key in ("market_outcomes_computed", "trading_return_metrics_computed", "strategy_logic_used", "old_m4_m5_2025_holdout_read", "runtime_admission_changed", "v1_state_boundary_changed", "v1_strength_semantics_changed", "production_authority", "fresh_oos"):
        assert r[key] is False


def test_post_x5f_decision_keeps_v1_and_x6_frozen():
    u = load("TREND_X4_POST_X5F_UPDATE_V1.json")
    assert u["updated_decision"] == "INSUFFICIENT_EVIDENCE"
    assert u["evidence_update"]["cross_carrier_normalized_strength_diagnostic"] == "SUPPORTED_RESEARCH_ONLY"
    assert u["evidence_update"]["stable_temporal_normalized_strength_representation"] == "NOT_ESTABLISHED"
    assert u["evidence_update"]["independent_regime_effect"] == "NOT_IDENTIFIED"
    assert u["representation_boundary"]["v1_strength"] == "UNCHANGED_abs_directional_score"
    assert u["representation_boundary"]["x5f_normalized_strength"] == "research_only_diagnostic_not_product_output"
    assert u["v1_action"] == "NO_CHANGE"
    assert u["x6_readiness"] == "HOLD_NOT_READY"
    assert u["runtime_admission_changed"] is False
    assert u["v1_parameter_changed"] is False
    assert u["production_authority"] is False
    assert u["fresh_oos"] is False


def test_handoff_and_roadmap_record_x5f_without_claiming_adoption():
    h = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    r = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (h, r):
        assert "X5F" in text
        assert "cross-carrier" in text
        assert "stable" in text.lower()
        assert "X6" in text and "HOLD" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
    assert "release/trend-regime-v1.0.0" in h
    assert "5a563d87d1628379e0d9a04aa7c5500bc30c4bc2" in h
