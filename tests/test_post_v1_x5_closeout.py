"""Fail-closed regression guards for Post-V1 X5/X5B closeout."""

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
    assert receipt["complete_window"] == {
        "start": "2026-08-17",
        "end": "2026-09-14",
        "trading_days": 21,
        "rows_per_carrier": 1008,
    }
    assert receipt["clock_contract"]["matches_m3_5m_offset0_clock"] is True
    assert receipt["clock_contract"]["bad_days_all_carriers"] == 0
    assert receipt["source_identity"]["DataHub_exact_source_identity"] is False
    assert receipt["source_identity"]["runtime_admission_effect"] == "none"
    assert receipt["market_outcome_statistics_computed_at_receipt_seal"] is False

    assert result["status"] == "X5_FIVE_CARRIER_5M_EXTERNAL_REPLICATION_COMPLETE"
    assert result["measurement"] == {
        "lookback_bars": 20,
        "estimator": "log_close_ols_slope_t@1.0",
        "t1": 2.0,
        "states": ["DOWN", "SIDEWAYS", "UP"],
        "strength": "abs(slope_t)",
    }
    assert [row["symbol"] for row in result["per_carrier"]] == [
        "000852.SH",
        "000688.SH",
        "000300.SH",
        "000905.SH",
        "000016.SH",
    ]
    assert all(row["input_rows"] == 1008 for row in result["per_carrier"])
    assert all(row["measurement_count"] == 989 for row in result["per_carrier"])
    assert result["sample_adequacy"]["all_predeclared_directional_horizon_origin_counts_at_least_50"] is True
    assert result["calibration_implication"]["carrier_specific_5m_t1_required_by_x5"] is False
    assert result["calibration_implication"]["overall_x4_decision_after_x5"] == "INSUFFICIENT_EVIDENCE"

    for key in (
        "market_outcomes_computed",
        "trading_return_metrics_computed",
        "parameter_tuning_performed",
        "runtime_admission_changed",
        "v1_parameter_changed",
        "production_authority",
        "fresh_oos",
    ):
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

    implication = result["calibration_implication"]
    assert implication["vendor_specific_5m_t1_required_by_x5b"] is False
    assert implication["source_identity_can_be_merged"] is False

    for key in (
        "parameter_tuning_performed",
        "trading_return_metrics_computed",
        "runtime_admission_changed",
        "v1_parameter_changed",
        "production_authority",
        "fresh_oos",
    ):
        assert result[key] is False


def test_post_x5_decision_keeps_x6_on_hold_and_v1_unchanged():
    update = load("TREND_X4_POST_X5_UPDATE_V1.json")

    assert update["status"] == "INSUFFICIENT_EVIDENCE_OVERALL_WITH_5M_CARRIER_AND_SOURCE_ROBUSTNESS"
    assert update["prior_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["updated_overall_decision"] == "INSUFFICIENT_EVIDENCE"
    assert update["calibration_family_status"]["INSUFFICIENT_EVIDENCE"] == "CURRENT_DECISION"
    assert update["calibration_family_status"]["INTERVAL_SPECIFIC_T1"].startswith("PLAUSIBLE_LEADING_CANDIDATE")
    assert update["v1_action"] == "NO_CHANGE"
    assert update["x6_readiness"] == "NOT_READY_FOR_SEMANTIC_VERSION_CHANGE"
    assert update["runtime_admission_changed"] is False
    assert update["v1_parameter_changed"] is False
    assert update["production_authority"] is False
    assert update["fresh_oos"] is False


def test_handoff_and_roadmap_reflect_x5b_closeout_without_claiming_x6_complete():
    handoff = (ROOT / "CONTINUE_HERE.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "docs" / "ROADMAP.md").read_text(encoding="utf-8")

    for text in (handoff, roadmap):
        assert "X5B" in text
        assert "X6" in text
        assert "HOLD" in text
        assert "INSUFFICIENT_EVIDENCE" in text
        assert "production_authority=false" in text
        assert "fresh_oos=false" in text

    assert "release/trend-regime-v1.0.0" in handoff
    assert "5a563d87d1628379e0d9a04aa7c5500bc30c4bc2" in handoff
