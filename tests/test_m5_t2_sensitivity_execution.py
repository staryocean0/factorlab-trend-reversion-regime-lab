import json
import subprocess
from pathlib import Path

from scripts.m5_v5_sensitivity_execution import SENSITIVITY_T2, sensitivity_label

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_EXECUTION_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
RESULT = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_sensitivity_contract_is_consumed_once_and_non_rescuing():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert payload["status"] == "CONSUMED_AFTER_ONE_T2_SENSITIVITY_RUN"
    assert payload["sensitivity_consumed"] is True
    assert payload["validation_rows_read_by_m5_5"] is True
    assert payload["holdout_rows_read"] is False
    assert payload["holdout_unlock_allowed"] is False
    assert tuple(payload["sensitivity_t2"]) == SENSITIVITY_T2 == (3.0, 5.0)
    assert payload["primary_t2_headline"] == 4.0
    assert payload["new_primary_family_created"] is False
    assert payload["primary_validation_rerun_allowed"] is False
    assert payload["sensitivity_rerun_allowed"] is False
    assert payload["replication_allowed_in_this_step"] is False
    assert payload["holdout_permanently_blocked_by_primary_support_rule"] is True


def test_primary_headline_remains_immutable_after_sensitivity():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    headline = "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS"
    assert primary["overall_conclusion"] == headline
    assert execution["primary_headline_conclusion"] == headline
    assert result["primary_headline_conclusion_unchanged"] == headline
    assert primary["holdout_unlocked"] is False
    assert result["holdout_unlocked"] is False


def test_sensitivity_locked_objects_still_match():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_sensitivity_run_and_result_are_frozen():
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert execution["pre_read_execution_contract_git_blob"] == "6d0a3f3217a1769f3736b2082635fdb6547785cf"
    assert execution["consumed_run"] == {
        "workflow_run_id": 34816576915,
        "head": "9e622c653a5510e73444a00f76881050946ffd1a",
        "artifact_id": 10336711547,
        "artifact_digest": "sha256:4c654375daa971c9aa028dc29fea1f1facab889cb29104a1b740f7e34efc575c",
        "result_receipt": "docs/governance/TREND_M5_T2_SENSITIVITY_V1.json",
    }
    assert result["status"] == "PASS_EXECUTED_SENSITIVITY_REINFORCES_PRIMARY_CONTRADICTION"
    assert result["overall_sensitivity_conclusion"] == "T2_3_AND_T2_5_ALL_EXECUTABLE_CONTRASTS_H1_CONTRADICTED"
    assert result["sensitivity_counts"] == {
        "planned_executable_contrasts": 8,
        "h1_contradicted": 8,
        "h1_direction": 0,
        "mixed_or_underpowered": 0,
    }
    assert all(row["status"] == "SENSITIVITY_H1_CONTRADICTED" for row in result["t2_3"] + result["t2_5"])


def test_sensitivity_labels_use_ci_direction_only():
    contradicted = {"primary_adequate": True, "primary_survival_5": {"ci95": [0.1, 0.2]}}
    h1_direction = {"primary_adequate": True, "primary_survival_5": {"ci95": [-0.2, -0.1]}}
    mixed = {"primary_adequate": True, "primary_survival_5": {"ci95": [-0.1, 0.1]}}
    underpowered = {"primary_adequate": False, "primary_survival_5": None}
    assert sensitivity_label(contradicted) == "SENSITIVITY_H1_CONTRADICTED"
    assert sensitivity_label(h1_direction) == "SENSITIVITY_H1_DIRECTION"
    assert sensitivity_label(mixed) == "SENSITIVITY_MIXED_OR_NULL"
    assert sensitivity_label(underpowered) == "SENSITIVITY_INCONCLUSIVE_UNDERPOWERED"
