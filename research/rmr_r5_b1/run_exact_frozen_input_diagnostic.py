#!/usr/bin/env python3
"""Execute the preregistered R5-B1 limited diagnostic on the exact frozen input."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import pandas as pd

import run_limited_diagnostic as diag

EXPECTED_DATA_SHA256 = "bea21fa9dd9532e21605511e07561b33d5569f86f69f5a487507531593b14c48"
EXPECTED_ROWS = 70114
EXPECTED_RUNNER_GIT_BLOB = "cd0ac94f7f8dc4fba7c9ee25701bcca02f551f2a"
SOURCE_COMMIT = "cf8397c12a9defa243dc272224dedebe6ccd3251"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def import_runner(path: Path):
    spec = importlib.util.spec_from_file_location("r5_frozen_exact", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen R5 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(data_path: Path, runner_path: Path) -> dict:
    actual_sha = sha256_file(data_path)
    if actual_sha != EXPECTED_DATA_SHA256:
        raise RuntimeError(f"frozen R5 data SHA mismatch: {actual_sha}")

    r5 = import_runner(runner_path)
    native = r5.load_native(data_path)
    if len(native) != EXPECTED_ROWS:
        raise RuntimeError(f"frozen R5 row mismatch: {len(native)}")

    returns = r5.build_continuous_returns(native)
    normalized = r5.add_causal_normalization(returns)
    state = r5.add_memory_state(normalized)
    frame = diag.eligible_B_frame(r5, state)
    train = frame.loc[frame["role"] == "TRAIN"].copy()
    val = frame.loc[frame["role"] == "VALIDATION"].copy()

    breadth = diag.daily_breadth(r5, train, val)
    shape = diag.monotonic_shape(train, val)
    survives = bool(breadth["supported"] and shape["supported"])
    adjudication = (
        "R5_B1_limited_diagnostic_supported_continue_TRAIN_VALIDATION_only"
        if survives
        else "R5_B1_limited_diagnostic_not_supported_close_B1"
    )

    return {
        "schema_id": "factorlab_r5_b1_exact_frozen_input_limited_diagnostic_receipt@1.0",
        "research_identity": "R5_multiscale_serial_dependence_state_v1_B1_limited_diagnostic",
        "input_mode": "exact_historical_frozen_input_migrated_to_owner_repository",
        "source_historical_commit": SOURCE_COMMIT,
        "source_runner_git_blob": EXPECTED_RUNNER_GIT_BLOB,
        "source_data_sha256": actual_sha,
        "source_rows": int(len(native)),
        "source_min_day": str(native["trading_day"].astype(str).min()),
        "source_max_day": str(native["trading_day"].astype(str).max()),
        "current_market_partition_equivalence": "not_established_and_not_used_for_diagnostic",
        "TRAIN_rows": int(len(train)),
        "VALIDATION_rows": int(len(val)),
        "daily_breadth": breadth,
        "anti_persistence_monotonic_shape": shape,
        "adjudication": adjudication,
        "BLACKBOX_read": False,
        "post_2020_rows_read": False,
        "PnL_read": False,
        "production_authority": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--frozen-runner", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.data, args.frozen_runner)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
