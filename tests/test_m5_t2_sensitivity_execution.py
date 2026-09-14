import json
import subprocess
from pathlib import Path

from scripts.m5_v5_sensitivity_execution import SENSITIVITY_T2, sensitivity_label

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_EXECUTION_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_sensitivity_contract_is_frozen_and_non_rescuing():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert payload["status"] == "FROZEN_BEFORE_SENSITIVITY_READ"
    assert payload["sensitivity_consumed"] is False
    assert payload["validation_rows_read_by_m5_5"] is False
    assert payload["holdout_rows_read"] is False
    assert payload["holdout_unlock_allowed"] is False
    assert tuple(payload["sensitivity_t2"]) == SENSITIVITY_T2 == (3.0, 5.0)
    assert payload["primary_t2_headline"] == 4.0
    assert payload["new_primary_family_created"] is False
    assert payload["primary_validation_rerun_allowed"] is False
    assert payload["replication_allowed_in_this_step"] is False


def test_primary_headline_is_immutable_before_sensitivity():
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert primary["overall_conclusion"] == execution["primary_headline_conclusion"]
    assert primary["overall_conclusion"] == "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS"
    assert primary["holdout_unlocked"] is False


def test_sensitivity_locked_objects_match():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_sensitivity_labels_use_ci_direction_only():
    contradicted = {"primary_adequate": True, "primary_survival_5": {"ci95": [0.1, 0.2]}}
    h1_direction = {"primary_adequate": True, "primary_survival_5": {"ci95": [-0.2, -0.1]}}
    mixed = {"primary_adequate": True, "primary_survival_5": {"ci95": [-0.1, 0.1]}}
    underpowered = {"primary_adequate": False, "primary_survival_5": None}
    assert sensitivity_label(contradicted) == "SENSITIVITY_H1_CONTRADICTED"
    assert sensitivity_label(h1_direction) == "SENSITIVITY_H1_DIRECTION"
    assert sensitivity_label(mixed) == "SENSITIVITY_MIXED_OR_NULL"
    assert sensitivity_label(underpowered) == "SENSITIVITY_INCONCLUSIVE_UNDERPOWERED"
