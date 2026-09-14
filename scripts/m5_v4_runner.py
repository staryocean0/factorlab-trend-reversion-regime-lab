from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from scripts.m5_v4_execution import execute_validation

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
SEAL = ROOT / "docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json"
EXECUTION = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def _preflight():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    seal = json.loads(SEAL.read_text(encoding="utf-8"))
    execution = json.loads(EXECUTION.read_text(encoding="utf-8"))
    if protocol["status"] != "FROZEN_BEFORE_M5_OUTCOMES":
        raise ValueError("M4 protocol is not frozen")
    if seal["status"] != "SEALED_BEFORE_PRIMARY_VALIDATION" or seal["next_allowed_step"]["milestone"] != "M5-4":
        raise ValueError("M5-4 is not authorized")
    if execution["status"] != "FROZEN_BEFORE_VALIDATION_READ" or execution["validation_consumed"]:
        raise ValueError("M5-4 execution contract is not available")
    for item in execution["locked_objects"]:
        if _git_blob(item["path"]) != item["git_blob"]:
            raise ValueError(f"locked object drift: {item['path']}")
    return protocol


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = execute_validation(ROOT, _preflight())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
