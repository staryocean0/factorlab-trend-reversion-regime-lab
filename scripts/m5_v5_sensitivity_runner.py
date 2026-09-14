from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.m5_v5_sensitivity_execution import execute_sensitivity

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
PRIMARY = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_V1.json"
PRIMARY_EXECUTION = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json"
EXECUTION = ROOT / "docs/governance/TREND_M5_T2_SENSITIVITY_EXECUTION_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def _preflight():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    primary = json.loads(PRIMARY.read_text(encoding="utf-8"))
    primary_execution = json.loads(PRIMARY_EXECUTION.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if protocol["status"] != "FROZEN_BEFORE_M5_OUTCOMES":
        raise ValueError("M4 protocol is not frozen")
    if primary["next_allowed_step"].split()[0] != "M5-5":
        raise ValueError("M5-5 is not authorized")
    if primary_execution["status"] != "CONSUMED_AFTER_ONE_PRIMARY_VALIDATION":
        raise ValueError("primary Validation state drift")
    if primary_execution["primary_validation_rerun_allowed"]:
        raise ValueError("primary Validation rerun must remain forbidden")
    if execution["status"] != "FROZEN_BEFORE_SENSITIVITY_READ" or execution["sensitivity_consumed"]:
        raise ValueError("M5-5 execution contract is not available")
    if execution["holdout_rows_read"] or execution["holdout_unlock_allowed"]:
        raise ValueError("Holdout must remain locked")
    for item in execution["locked_objects"]:
        if _git_blob(item["path"]) != item["git_blob"]:
            raise ValueError(f"locked object drift: {item['path']}")
    return protocol, primary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    protocol, primary = _preflight()
    payload = execute_sensitivity(ROOT, protocol, primary)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
