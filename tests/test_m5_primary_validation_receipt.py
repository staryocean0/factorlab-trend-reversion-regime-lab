import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
EXECUTION = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json"


def test_primary_validation_was_consumed_once_and_holdout_stays_locked():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert result["status"] == "PASS_EXECUTED_H1_CONTRADICTED"
    assert result["overall_conclusion"] == "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS"
    assert result["supporting_contrasts"] == []
    assert result["holdout_rows_read"] is False
    assert result["holdout_unlocked"] is False
    assert result["holdout_permanently_blocked_by_primary_support_rule"] is True
    assert result["sensitivity_t2_3_5_run"] is False
    assert result["replication_000688_run"] is False
    assert execution["status"] == "CONSUMED_AFTER_ONE_PRIMARY_VALIDATION"
    assert execution["validation_consumed"] is True
    assert execution["primary_validation_rerun_allowed"] is False
    assert execution["holdout_rows_read"] is False


def test_all_executable_primary_contrasts_contradict_h1():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    contrasts = result["executable_primary_contrasts"]
    assert [(x["interval"], x["direction"]) for x in contrasts] == [("1m","UP"),("1m","DOWN"),("5m","UP"),("5m","DOWN")]
    for item in contrasts:
        assert item["status"] == "H1_CONTRADICTED"
        assert item["strong_minus_moderate"] > 0.35
        assert item["ci95"][0] > 0.0
        assert item["raw_p"] == 1.0
        assert item["holm_adjusted_p"] == 1.0
        assert item["reversal10_strong_minus_moderate"] < -0.20
        assert item["reversal10_ci95"][1] < 0.0


def test_not_admitted_contrasts_stay_in_eight_member_family():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    not_admitted = result["not_admitted_primary_contrasts"]
    assert len(result["executable_primary_contrasts"]) + len(not_admitted) == 8
    assert {(x["interval"], x["direction"]) for x in not_admitted} == {("15m","UP"),("15m","DOWN"),("60m","UP"),("60m","DOWN")}
    assert all(x["raw_p"] == 1.0 and x["holm_adjusted_p"] == 1.0 for x in not_admitted)


def test_result_artifact_identity_is_frozen():
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    assert result["execution_contract_pre_read_git_blob"] == "4fa6b5eee9582be7b147abf52988f01d3254a672"
    assert result["run"] == {
        "workflow_run_id": 34814912150,
        "head": "4aecd9b88a171eb51a63462bfe10eaa8168f34dc",
        "artifact_id": 10335368583,
        "artifact_digest": "sha256:acf170aab180478c73fb2dcc09ec5610c06e7276e566ee2fc7a134082e2dc045",
    }
