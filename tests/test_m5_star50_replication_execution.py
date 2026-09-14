import json
import subprocess
from pathlib import Path

from scripts.m5_v6_replication_execution import CARRIER, PROFILES, replication_label

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "docs/governance/TREND_M5_STAR50_REPLICATION_EXECUTION_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
SENSITIVITY = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_replication_contract_is_frozen_before_read():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert payload["status"] == "FROZEN_BEFORE_REPLICATION_READ"
    assert payload["replication_consumed"] is False
    assert payload["replication_rows_read"] is False
    assert payload["holdout_rows_read"] is False
    assert payload["holdout_unlock_allowed"] is False
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


def test_replication_profiles_and_labels_are_fixed():
    assert PROFILES == {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [0.1, 0.2]}}) == "REPLICATION_H1_CONTRADICTED"
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [-0.2, -0.1]}}) == "REPLICATION_H1_DIRECTION"
    assert replication_label({"primary_adequate": True, "primary_survival_5": {"ci95": [-0.1, 0.1]}}) == "REPLICATION_MIXED_OR_NULL"
    assert replication_label({"primary_adequate": False, "primary_survival_5": None}) == "REPLICATION_INCONCLUSIVE_UNDERPOWERED"
