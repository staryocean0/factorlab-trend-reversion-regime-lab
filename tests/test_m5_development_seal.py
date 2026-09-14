import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEAL = ROOT / "docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "hash-object", str(ROOT / path)],
        text=True,
    ).strip()


def test_m5_development_seal_is_pre_validation_and_immutable():
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    assert seal["schema_id"] == "trend_m5_development_seal@1.0"
    assert seal["status"] == "SEALED_BEFORE_PRIMARY_VALIDATION"
    assert seal["validation_rows_read"] is False
    assert seal["holdout_rows_read"] is False
    assert seal["validation_run_performed"] is False
    assert seal["holdout_run_performed"] is False
    assert seal["h1_adjudicated"] is False
    assert seal["protocol_change_allowed"] is False
    assert seal["next_allowed_step"]["milestone"] == "M5-4"
    assert seal["next_allowed_step"]["holdout_still_locked"] is True


def test_all_sealed_git_objects_still_match():
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    locked = [*seal["sealed_contracts"], *seal["sealed_code"]]
    locked.append({
        "path": seal["sealed_data_identity"]["local_manifest_path"],
        "git_blob": seal["sealed_data_identity"]["local_manifest_git_blob"],
    })
    for item in locked:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_development_run_and_source_identity_are_frozen():
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    run = seal["sealed_development_run"]
    assert run == {
        "workflow_run_id": 34812469153,
        "head": "7069d2afc1c2137c14a16003dcfd5ebf9c21376f",
        "artifact_id": 10334954106,
        "artifact_digest": "sha256:95eb49298359959cd4ebf82fc21eca8d79e61e932f0d550fbb3c09efd56b3147",
        "development_start": "2020-07-23",
        "development_end": "2022-12-30",
    }
    data = seal["sealed_data_identity"]
    assert data["admitted_profiles"] == ["trend_1m_official_v1", "trend_5m_offset0_v1"]
    assert data["not_admitted_anchor_intervals"] == ["15m", "60m"]
    assert data["views"]["1m_official"] == "aeacff04b268c166faac333ec7ab9d840abcd347d82cb3bcee0218d058fc7423"
    assert data["views"]["5m_offset_0"] == "d3101e6adf7a3e85b11f7c3503a6161f3ab363f7edd90ac8cba451ffe409c46a"
