from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.m5_v6_replication_execution import execute_replication

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
ADMISSION = ROOT / "docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
SENSITIVITY = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_V1.json"
EXECUTION = ROOT / "docs/governance/TREND_M5_STAR50_REPLICATION_EXECUTION_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def _preflight():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    sensitivity = json.loads(SENSITIVITY.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if protocol["status"] != "FROZEN_BEFORE_M5_OUTCOMES":
        raise ValueError("M4 protocol is not frozen")
    if primary["overall_conclusion"] != "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS":
        raise ValueError("primary headline drift")
    if sensitivity["next_allowed_step"].split()[0] != "M5-6":
        raise ValueError("M5-6 is not authorized")
    if execution["status"] != "FROZEN_BEFORE_REPLICATION_READ" or execution["replication_consumed"]:
        raise ValueError("M5-6 execution contract is not available")
    if execution["holdout_rows_read"] or execution["holdout_unlock_allowed"]:
        raise ValueError("Holdout must remain locked")
    admitted = {(x["carrier"], x["profile_id"]): x["status"] for x in admission["anchor_admission"]}
    for profile_id in ("trend_1m_official_v1", "trend_5m_offset0_v1"):
        if admitted.get(("000688.SH", profile_id)) != "ADMITTED":
            raise ValueError(f"STAR50 profile not admitted: {profile_id}")
    for item in execution["locked_objects"]:
        if _git_blob(item["path"]) != item["git_blob"]:
            raise ValueError(f"locked object drift: {item['path']}")
    return protocol, primary, sensitivity


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol, primary, sensitivity = _preflight()
    payload = execute_replication(ROOT, protocol, primary, sensitivity)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
