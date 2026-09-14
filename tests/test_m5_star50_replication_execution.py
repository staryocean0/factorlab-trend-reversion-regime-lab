import json
import subprocess
from pathlib import Path

from scripts.m5_v6_replication_execution import CARRIER, PROFILES, replication_label

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "docs/governance/TREND_M5_STAR50_REPLICATION_EXECUTION_V1.json"
RECEIPT = ROOT / "docs/governance/TREND_M5_STAR50_REPLICATION_V1.json"
CLOSEOUT = ROOT / "docs/governance/TREND_M5_CLOSEOUT_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
SENSITIVITY = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_replication_contract_is_consumed_once_and_holdout_stays_closed():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert payload["status"] == "CONSUMED_AFTER_ONE_STAR50_REPLICATION"
    assert payload["replication_consumed"] is True
    assert payload["replication_rows_read"] is True
    assert payload["replication_rerun_allowed"] is False
    assert payload["holdout_rows_read"] is False
    assert payload["holdout_unlock_allowed"] is False
    assert payload["holdout_permanently_blocked_by_primary_support_rule"] is True
    assert payload["m5_outcome_work_reopen_allowed"] is False
    assert payload["carrier"] == CARRIER == "000688.SH"
    assert payload["t2"] == 4.0
    assert payload["new_primary_family_created"] is False
    assert payload["pooling_with_csi1000_allowed"] is False
    assert payload["primary_headline_change_allowed"] is False
    assert payload["phase_profiles_executable"] is False


def test_prior_results_remain_non_rescuable():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    sensitivity = json.loads(SENSITIVITY.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert primary["overall_conclusion"] == execution["csi1000_primary_headline"]
    assert sensitivity["overall_sensitivity_conclusion"] == "T2_3_AND_T2_5_ALL_EXECUTABLE_CONTRASTS_H1_CONTRADICTED"
    assert primary["holdout_unlocked"] is False
    assert execution["primary_validation_rerun_allowed"] is False
    assert execution["sensitivity_rerun_allowed"] is False


def test_replication_locked_objects_match():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_replication_receipt_is_clear_and_separate():
    payload = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_EXECUTED_CLEAR_QUALITATIVE_REPLICATION"
    assert payload["overall_replication_conclusion"] == "CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION"
    assert payload["replication_counts"] == {
        "executable_contrasts": 4,
        "point_estimate_same_direction": 4,
        "statistically_clear_same_direction": 4,
        "statistically_clear_opposite_direction": 0,
        "h1_contradicted": 4,
        "h1_direction": 0,
    }
    assert payload["remaining_robustness_reporting"]["phase_sensitivity_profiles"] == "NOT_ADMITTED_NOT_EXECUTED"
    assert payload["remaining_robustness_reporting"]["anchor_15m_60m"] == "NOT_ADMITTED_NOT_EXECUTED"
    assert payload["remaining_robustness_reporting"]["pooling_with_csi1000"] is False
    assert payload["holdout_rows_read"] is False
    assert payload["holdout_unlocked"] is False
    for item in payload["executable_replication_contrasts"]:
        assert item["status"] == "REPLICATION_H1_CONTRADICTED"
        assert item["strong_minus_moderate"] > 0.0
        assert item["ci95"][0] > 0.0
        assert item["reversal10_strong_minus_moderate"] < 0.0
        assert item["reversal10_ci95"][1] < 0.0


def test_m5_closeout_is_complete_and_only_m6_is_next():
    payload = json.loads(CLOSEOUT.read_text(encoding="utf-8"))
    assert payload["status"] == "M5_COMPLETE_H1_CONTRADICTED_ROBUST_ON_ADMITTED_1M_5M"
    assert len(payload["evidence_chain"]) == 6
    assert payload["scope_limits"]["admitted_intervals"] == ["1m", "5m"]
    assert payload["scope_limits"]["not_admitted_anchor_intervals"] == ["15m", "60m"]
    assert payload["scope_limits"]["phase_sensitivity_profiles"] == "NOT_ADMITTED_NOT_EXECUTED"
    assert payload["scope_limits"]["holdout_opened"] is False
    assert payload["scope_limits"]["local_resampling_used"] is False
    assert payload["scope_limits"]["carrier_pooling_used"] is False
    assert payload["m5_outcome_work_reopen_allowed"] is False
    assert payload["next_allowed_step"] == "M6 representation decision only"
    assert payload["representation_decision_pending"] is True
    assert payload["trading_semantics"] is False


def test_replication_profiles_and_labels_are_fixed():
    assert PROFILES == {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [0.1, 0.2]}}) == "REPLICATION_H1_CONTRADICTED"
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [-0.2, -0.1]}}) == "REPLICATION_H1_DIRECTION"
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [-0.1, 0.1]}}) == "REPLICATION_MIXED_OR_NULL"
    assert replication_label({"primary_adequate": False, "primary_survival_5": None}) == "REPLICATION_INCONCLUSIVE_UNDERPOWERED"
