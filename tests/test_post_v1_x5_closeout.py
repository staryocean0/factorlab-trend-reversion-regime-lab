"""Fail-closed regression guards for Post-V1 X5 through X5E closeout."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "docs" / "governance"


def load(name: str) -> dict:
    return json.loads((GOV / name).read_text(encoding="utf-8"))


def test_x5_five_carrier_replication_is_research_only_and_fixed_parameter():
    receipt = load("TREND_X5_SINA_SOURCE_RECEIPT_V1.json")
    result = load("TREND_X5_FIVE_CARRIER_5M_RESULT_V1.json")
    assert receipt["status"] == "SOURCE_ACQUIRED_CLOCK_GATE_PASS_BEFORE_STATISTICS"
    assert receipt["period"] == "5m"
    assert receipt["complete_window"] == {"start": "2026-08-17", "end": "2026-09-14", "trading_days": 21, "rows_per_carrier": 1008}
    assert receipt["clock_contract"]["matches_m3_5m_offset0_clock"] is True
    assert receipt["clock_contract"]["bad_days_all_carriers"] == 0
    assert receipt["source_identity"]["DataHub_exact_source_identity"] is False
    assert receipt["source_identity"]["runtime_admission_effect"] == "none"
    assert receipt["market_outcome_statistics_computed_at_receipt_seal"] is False
    assert result["status"] == "X5_FIVE_CARRIER_5M_EXTERNAL_REPLICATION_COMPLETE"
    assert result["measurement"] == {"lookback_bars": 20, "estimator": "log_close_ols_slope_t@1.0", "t1": 2.0, "states": ["DOWN", "SIDEWAYS", "UP"], "strength": "abs(slope_t)"}
    assert [row["symbol"] for row in result["per_carrier"]] == ["000852.SH", "000688.SH", "000300.SH", "000905.SH", "000016.SH"]
    assert all(row["input_rows"] == 1008 for row in result["per_carrier"])
    assert all(row["measurement_count"] == 989 for row in result["per_carrier"])
    assert result["sample_adequacy"]["all_predeclared_directional_horizon_origin_counts_at_least_50"] is True
    assert result["calibration_implication"]["carrier_specific_5m_t1_required_by_x5"] is False
    assert result["calibration_implication"]["overall_x4_decision_after_x5"] == "INSUFFICIENT_EVIDENCE"
    for key in ("market_outcomes_computed", "trading_return_metrics_computed", "parameter_tuning_performed", "runtime_admission_changed", "v1_parameter_changed", "production_authority", "fresh_oos"):
        assert result[key] is False


def test_x5b_source_robustness_does_not_merge_source_identity_or_change_v1():
    freeze = load("TREND_X5B_SOURCE_ROBUSTNESS_FREEZE_V1.json")
    result = load("TREND_X5B_SOURCE_ROBUSTNESS_RESULT_V1.json")
    assert freeze["status"] == "FROZEN_BEFORE_SOURCE_ROBUSTNESS_STATISTICS"
    assert freeze["fixed_measurement"]["lookback_bars"] == 20
    assert freeze["fixed_measurement"]["t1"] == 2.0
    assert freeze["runtime_admission_changed"] is False
    assert freeze["v1_parameter_changed"] is False
    assert result["status"] == "SOURCE_ROBUST_FOR_5M_STATE_SEMANTICS"
    assert result["decision_rule_pass"] is True
    assert len(result["results"]) == 2
    for row in result["results"]:
        assert row["common_close_rows"] == 1008
        assert row["measurement_count"] == 989
        assert row["missing_sina"] == 0
        assert row["missing_eastmoney"] == 0
        assert row["slope_t_pearson"] > 0.99999
        assert row["slope_t_abs_diff_q95"] < 0.004
        assert row["state_exact_agreement"] == 1.0
        assert row["state_disagreement_count"] == 0
        assert row["opposite_direction_disagreement_count"] == 0
    assert result["calibration_implication"]["vendor_specific_5m_t1_required_by_x5b"] is False
    assert result["calibration_implication"]["source_identity_can_be_merged"] is False
    for key in ("parameter_tuning_performed", "trading_return_metrics_computed", "runtime_admission_changed", "v1_parameter_changed", "production_authority", "fresh_oos"):
        assert result[key] is False


def test_post_x5_decision_keeps_x6_on_hold_and_v1_unchanged():
    update = load("TREND_X4_POST_X5_UPDATE_V1.json")
    assert update["status"] == "INSUFFICIENT_EVIDENCE_OVERALL_WITH_5M_CARRIER_AND_SOURCE_ROBUSTNESS"
    assert update["prior_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["calibration_family_status"]["INSUFFICIENT_EVIDENCE"] == "CURRENT_DECISION"
    assert update["v1_action"] == "NO_CHANGE"
    assert update["runtime_admission_changed"] is False
    assert update["v1_parameter_changed"] is False
    assert update["production_authority"] is False
    assert update["fresh_oos"] is False


def test_x5c_resolves_60m_underpower_but_keeps_public_clock_research_only():
    protocol = load("TREND_X5C_15M_60M_CROSS_CARRIER_PROTOCOL_V1.json")
    receipt = load("TREND_X5C_SINA_15M_60M_SOURCE_RECEIPT_V1.json")
    result = load("TREND_X5C_15M_60M_CROSS_CARRIER_RESULT_V1.json")
    assert protocol["status"] == "FROZEN_BEFORE_NEW_X5C_STATISTICS"
    assert protocol["fixed_measurement_first"]["lookback_bars"] == 20
    assert protocol["fixed_measurement_first"]["t1"] == 2.0
    assert receipt["status"] == "SOURCE_ACQUIRED_CLOCK_QC_PASS_BEFORE_X5C_STATISTICS"
    assert receipt["views"]["15m_native"]["m3_exact_profile_identity"] is False
    assert receipt["views"]["60m_native"]["m3_exact_profile_identity"] is False
    assert receipt["views"]["60m_native"]["complete_window"]["trading_days"] == 170
    assert receipt["views"]["60m_native"]["old_m4_m5_2025_holdout_included"] is False
    assert result["status"] == "X5C_COMPLETE_15M_RELATIVELY_STABLE_60M_MATERIALLY_HETEROGENEOUS"
    assert result["five_carrier_full_windows"]["60m_native"]["minimum_directional_metric_origins"] >= 100
    d15 = result["cross_carrier_dispersion_full_window"]["15m"]
    d60 = result["cross_carrier_dispersion_full_window"]["60m"]
    assert d60["abs_slope_t_q90_range"] > d15["abs_slope_t_q90_range"]
    assert d60["sideways_occupancy_range"] > d15["sideways_occupancy_range"]
    assert result["x5d_readiness"]["adequate_60m_support"] is True
    for key in ("market_return_outcomes_computed", "trading_return_metrics_computed", "parameter_tuning_performed", "runtime_admission_changed", "v1_parameter_changed", "production_authority", "fresh_oos"):
        assert result[key] is False


def test_x5d_parameters_are_dev_only_and_external_comparison_does_not_select_static_calibration():
    protocol = load("TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_PROTOCOL_V1.json")
    method = load("TREND_X5D_DEVELOPMENT_CALIBRATION_METHOD_V1.json")
    receipt = load("TREND_X5D_DEVELOPMENT_CALIBRATION_RECEIPT_V1.json")
    result = load("TREND_X5D_INTERVAL_CALIBRATION_COMPARISON_RESULT_V1.json")
    assert protocol["status"] == "FROZEN_BEFORE_X5D_COMPARISON"
    assert method["status"] == "FROZEN_BEFORE_DEVELOPMENT_SCORE_READ"
    assert method["development_window"] == {"start": "2020-07-23", "end": "2020-12-31", "old_m4_m5_2025_holdout_included": False}
    assert receipt["status"] == "DEVELOPMENT_PARAMETERS_SEALED_BEFORE_CANDIDATE_EXTERNAL_EVALUATION"
    audit = receipt["separation_audit"]
    assert audit["prior_2026_raw_v1_data_used_to_fit_any_x5d_parameter"] is False
    assert audit["candidate_transformed_2026_evaluation_computed_before_this_receipt"] is False
    assert audit["trading_returns_read_or_used"] is False
    assert receipt["interval_specific_t1"]["60m"]["t1"] < 1.3
    assert 1.2 < receipt["normalization_primary_median_abs"]["equivalent_raw_t1"]["60m"] < 1.4
    assert result["status"] == "X5D_COMPLETE_NO_STATIC_CALIBRATION_FAMILY_DOMINATES"
    assert result["selected_outcome"] == "INSUFFICIENT_EVIDENCE"
    assert result["semantic_dispersion_comparison_vs_v1"]["any_pairwise_strict_pareto_dominance_among_all_candidates"] is False
    assert result["semantic_dispersion_comparison_vs_v1"]["INTERVAL_SPECIFIC_T1"]["worsened"] > 0
    assert result["semantic_dispersion_comparison_vs_v1"]["NORMALIZED_MEDIAN_ABS"]["worsened"] > 0
    assert result["key_60m_external_metrics"]["INTERVAL_SPECIFIC_T1"]["max_state_change_vs_v1"] > 0.10
    assert result["v1_action"] == "NO_CHANGE"
    assert result["x6_readiness"] == "NOT_READY_FOR_SEMANTIC_VERSION_CHANGE"
    for key in ("runtime_admission_changed", "v1_parameter_changed", "production_authority", "fresh_oos"):
        assert result[key] is False


def test_post_x5d_decision_keeps_x6_hold():
    update = load("TREND_X4_POST_X5D_UPDATE_V1.json")
    assert update["status"] == "INSUFFICIENT_EVIDENCE_STATIC_INTERVAL_CALIBRATION_NOT_ADOPTED"
    assert update["updated_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["current_family_status"]["INTERVAL_SPECIFIC_T1"] == "STATIC_FORM_NOT_SUPPORTED_FOR_ADOPTION"
    assert update["current_family_status"]["STATIC_NORMALIZED_SCORE_PLUS_UNIVERSAL_THRESHOLD"] == "NOT_SUPPORTED_FOR_ADOPTION_STATE_SEMANTICS_MIXED"
    assert update["v1_action"] == "NO_CHANGE"
    assert update["x6_readiness"] == "HOLD_NOT_READY"


def test_x5e_is_strictly_causal_and_does_not_refit_on_2026():
    protocol = load("TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_PROTOCOL_V1.json")
    assert protocol["status"] == "FROZEN_BEFORE_X5E_STATISTICS"
    assert protocol["scope"]["interval"] == "60m"
    assert protocol["scope"]["old_2025_holdout_read"] is False
    assert protocol["frozen_measurement"]["lookback_bars"] == 20
    assert protocol["frozen_measurement"]["v1_raw_t1"] == 2.0
    causal = protocol["causal_normalization"]
    assert causal["primary_scale_estimator"] == "rolling_median_abs_prior_scores"
    assert causal["candidate_windows_measurements"] == [40, 80, 120]
    assert causal["causality"] == "scale_at_t_uses_only_scores_strictly_before_t"
    assert causal["normalized_semantic_threshold"] == 0.44780633341059867
    assert causal["no_2026_parameter_fit"] is True
    assert protocol["fair_evaluation"]["common_warmup"] == 120
    assert protocol["decision_rule"]["if_candidates_trade_off_metrics"] == "INSUFFICIENT_EVIDENCE_NO_V1_CHANGE"
    assert protocol["decision_rule"]["x6_default"] == "HOLD"


def test_x5e_establishes_temporal_scale_drift_but_rejects_dynamic_state_boundary_adoption():
    result = load("TREND_X5E_60M_TEMPORAL_SCALE_CAUSAL_NORMALIZATION_RESULT_V1.json")
    assert result["status"] == "TEMPORAL_SCALE_NONSTATIONARITY_ESTABLISHED_CAUSAL_NORMALIZATION_NOT_ADOPTED"
    scope = result["scope"]
    assert scope["source_is_m3_datahub_exact_identity"] is False
    assert scope["input_rows_per_carrier"] == 680
    assert scope["raw_measurements_per_carrier"] == 661
    assert scope["common_evaluation_measurements_per_carrier"] == 541
    ratios = result["raw_temporal_scale_evidence"]["by_carrier"]
    assert len(ratios) == 5
    assert min(ratios.values()) > 1.6
    base_range = result["common_window_baseline"]["V1_RAW"]["cross_carrier_median_strength_range"]
    assert base_range > 1.4
    candidates = result["causal_candidates"]
    assert set(candidates) == {"CAUSAL_MEDABS_40", "CAUSAL_MEDABS_80", "CAUSAL_MEDABS_120"}
    for candidate in candidates.values():
        assert candidate["strict_semantic_pareto_dominates_v1"] is False
        assert candidate["cross_carrier_median_strength_range"] < 0.11
        assert candidate["cross_carrier_strength_range_reduction_vs_raw"] > 0.92
        assert candidate["opposite_direction_disagreement_count_all_carriers"] == 0
        assert len(candidate["semantic_worsened_vs_v1"]) > 0
    findings = result["findings"]
    assert findings["temporal_scale_nonstationarity"] == "SUPPORTED_ON_THIS_2026_WINDOW"
    assert findings["cross_carrier_strength_normalization"] == "STRONGLY_IMPROVED_BY_ALL_CAUSAL_WINDOWS"
    assert findings["within_carrier_temporal_strength_stability"] == "NOT_CONSISTENTLY_IMPROVED"
    assert findings["state_boundary_semantics"] == "TRADE_OFFS_NO_PARETO_DOMINANCE"
    decision = result["decision"]
    assert decision["causal_state_boundary_normalization"] == "NOT_SUPPORTED_FOR_ADOPTION"
    assert decision["causal_strength_scale_normalization"] == "PROMISING_FOR_CROSS_CARRIER_DIAGNOSTICS_TEMPORAL_STABILITY_NOT_ESTABLISHED"
    assert decision["v1_action"] == "NO_CHANGE"
    assert decision["x6"] == "HOLD_NOT_READY"
    for key in ("trading_returns_computed", "strategy_metrics_computed", "runtime_admission_changed", "v1_parameter_changed", "old_m4_m5_2025_holdout_read", "production_authority", "fresh_oos"):
        assert result[key] is False


def test_post_x5e_decision_and_handoff_keep_x6_hold():
    update = load("TREND_X4_POST_X5E_UPDATE_V1.json")
    assert update["status"] == "TEMPORAL_NONSTATIONARITY_CONFIRMED_CAUSAL_NORMALIZATION_DIAGNOSTIC_ONLY"
    assert update["prior_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    families = update["calibration_family_status"]
    assert families["CAUSAL_STATE_BOUNDARY_NORMALIZATION"] == "NOT_SUPPORTED_FOR_ADOPTION_BY_X5E"
    assert families["CAUSAL_STRENGTH_SCALE_NORMALIZATION"] == "PROMISING_CROSS_CARRIER_DIAGNOSTIC_TEMPORAL_STABILITY_NOT_ESTABLISHED"
    assert families["INSUFFICIENT_EVIDENCE"] == "CURRENT_DECISION"
    assert update["v1_action"] == "NO_CHANGE"
    assert update["x6_readiness"] == "NOT_READY_FOR_SEMANTIC_VERSION_CHANGE"
    assert update["runtime_admission_changed"] is False
    assert update["v1_parameter_changed"] is False
    assert update["production_authority"] is False
    assert update["fresh_oos"] is False
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")
    for text in (handoff, roadmap):
        assert "X5B" in text
        assert "X5C" in text
        assert "X5D" in text
        assert "X5E" in text
        assert "X6" in text
        assert "HOLD" in text
        assert "INSUFFICIENT_EVIDENCE" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text
    assert "release/trend-regime-v1.0.0" in handoff
    assert "5a563d87d1628379e0d9a04aa7c5500bc30c4bc2" in handoff
