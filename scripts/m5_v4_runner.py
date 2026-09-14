from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from factor_lab.market_state.trend_regime_profiles import resolve_trend_profile
from regime_lab.market_data import load_market_data
from scripts.m5_development_adequacy_core import build_state_series
from scripts.m5_primary_validation_core import analyze_profile
from scripts.m5_validation_bootstrap import holm_adjust
from scripts.m5_validation_durations import duration_summaries

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
SEAL = ROOT / "docs/governance/TREND_M5_DEVELOPMENT_SEAL_V1.json"
EXECUTION = ROOT / "docs/governance/TREND_M5_PRIMARY_VALIDATION_EXECUTION_V1.json"
CARRIER = "000852.SH"
CONTEXT_START = "2022-12-30"
PROFILES = {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
PLANNED = (("1m", "UP"), ("1m", "DOWN"), ("5m", "UP"), ("5m", "DOWN"), ("15m", "UP"), ("15m", "DOWN"), ("60m", "UP"), ("60m", "DOWN"))


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def _assert_locked_objects(contract):
    for item in contract["locked_objects"]:
        if _git_blob(item["path"]) != item["git_blob"]:
            raise ValueError(f"locked object drift: {item['path']}")


def _identity(frame, column: str, expected: str | None = None):
    if column not in frame.columns or frame[column].dropna().empty:
        raise ValueError(f"missing identity column: {column}")
    values = sorted({str(value) for value in frame[column].dropna().unique()})
    if expected is not None and values != [expected]:
        raise ValueError(f"{column} drift")
    return values


def _secondary_rule(block):
    reversal = block["secondary_reversal_10"]
    ret5 = block["secondary_return_5"]
    reversal_h1 = bool(block["reversal_adequate"] and reversal and reversal["strong_minus_moderate"] > 0.0)
    return_h1 = bool(block["return_adequate"] and ret5 and ret5["strong_minus_moderate"] < 0.0)
    reversal_clear_opposite = bool(block["reversal_adequate"] and reversal and reversal["ci95"][1] < 0.0)
    return_clear_opposite = bool(block["return_adequate"] and ret5 and ret5["ci95"][0] > 0.0)
    return {
        "reversal_has_h1_direction": reversal_h1,
        "return_has_h1_direction": return_h1,
        "reversal_statistically_clear_opposite": reversal_clear_opposite,
        "return_statistically_clear_opposite": return_clear_opposite,
        "passes": (reversal_h1 or return_h1) and not reversal_clear_opposite and not return_clear_opposite,
    }


def main():
    print("M5 validation runner")


if __name__ == "__main__":
    main()
