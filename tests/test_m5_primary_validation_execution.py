import json
import subprocess
from pathlib import Path

from scripts.m5_validation_bootstrap import BOOTSTRAP_REPLICATES, BOOTSTRAP_SEED, HOLM_FAMILY_SIZE, cluster_bootstrap_difference, holm_adjust
from scripts.m5_v4_execution import PLANNED, PROFILES, secondary_rule

ROOT = Path(__file__).resolve().parents[1]
EXECUTION = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json"


def _git_blob(path):
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_execution_contract_is_frozen_before_read():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    assert payload["status"] == "FROZEN_BEFORE_VALIDATION_READ"
    assert payload["validation_consumed"] is False
    assert payload["validation_rows_read"] is False
    assert payload["holdout_rows_read"] is False
    assert payload["carrier"] == "000852.SH"
    assert payload["primary_t2"] == 4.0
    assert (payload["validation_start"], payload["validation_end"], payload["context_start"]) == ("2023-01-03", "2024-12-31", "2022-12-30")
    assert payload["planned_primary_family_size"] == 8
    assert payload["not_admitted_raw_p"] == 1.0
    assert payload["holm_alpha"] == 0.05
    assert payload["bootstrap_replicates"] == BOOTSTRAP_REPLICATES == 5000
    assert payload["bootstrap_seed"] == BOOTSTRAP_SEED == 20260914


def test_validation_code_and_prior_seal_objects_are_immutable():
    payload = json.loads(EXECUTION.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_primary_family_cannot_shrink_after_admission():
    assert HOLM_FAMILY_SIZE == 8
    assert len(PLANNED) == 8
    assert PROFILES == {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
    raw = [0.001, 0.01, 0.02, 0.03, 1.0, 1.0, 1.0, 1.0]
    adjusted = holm_adjust(raw)
    assert len(adjusted) == 8
    assert adjusted[4:] == [1.0, 1.0, 1.0, 1.0]
    assert adjusted[0] >= raw[0]


def test_cluster_bootstrap_is_deterministic_and_directional():
    records = []
    for week in range(1, 21):
        for _ in range(8):
            records.append({"week": f"2024-W{week:02d}", "group": "MODERATE", "metric": 0.80})
            records.append({"week": f"2024-W{week:02d}", "group": "STRONG", "metric": 0.60})
    first = cluster_bootstrap_difference(records, "metric", alternative="less")
    second = cluster_bootstrap_difference(records, "metric", alternative="less")
    assert first == second
    assert first["strong_minus_moderate"] < 0
    assert first["one_sided_bootstrap_p"] < 0.05


def test_secondary_rule_requires_h1_direction_without_clear_opposite():
    block = {
        "reversal_adequate": True,
        "return_adequate": True,
        "secondary_reversal_10": {"strong_minus_moderate": 0.03, "ci95": [-0.01, 0.08]},
        "secondary_return_5": {"strong_minus_moderate": -0.002, "ci95": [-0.006, 0.001]},
    }
    assert secondary_rule(block)["passes"] is True
