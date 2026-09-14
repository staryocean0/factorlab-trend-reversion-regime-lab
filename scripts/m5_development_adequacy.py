"""M5-2 Development-only sample adequacy entrypoint."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from factor_lab.market_state.trend_regime_profiles import resolve_trend_profile
from regime_lab.market_data import load_market_data
from scripts.m5_development_adequacy_core import build_state_series, episode_adequacy

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
ADMISSION = ROOT / "docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json"
START, END = "2020-07-23", "2022-12-30"
PROFILES = {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
CARRIERS = ("000852.SH", "000688.SH")


def _identity(frame, column: str, expected: str | None = None):
    if column not in frame.columns or frame[column].dropna().empty:
        raise ValueError(f"missing identity column: {column}")
    values = sorted({str(value) for value in frame[column].dropna().unique()})
    if expected is not None and values != [expected]:
        raise ValueError(f"{column} drift: {values} != {[expected]}")
    return values


def run():
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    admission = json.loads(ADMISSION.read_text(encoding="utf-8"))
    next_step = admission["next_allowed_step"]
    if protocol["status"] != "FROZEN_BEFORE_M5_OUTCOMES" or next_step["milestone"] != "M5-2":
        raise ValueError("M5-2 is not authorized")
    if not next_step["validation_outcomes_still_locked"] or not next_step["holdout_outcomes_still_locked"]:
        raise ValueError("future splits must remain locked")

    t1 = float(protocol["state_scheme"]["t1"])
    t2 = float(protocol["state_scheme"]["primary_t2"])
    results = []
    for carrier in CARRIERS:
        for profile_id, frequency in PROFILES.items():
            profile = resolve_trend_profile(bar_interval=frequency, profile_id=profile_id)
            frame = load_market_data(carrier, frequency, START, END, root=ROOT)
            view_ids = _identity(frame, "export_view_id", profile.layer1_view_id)
            frequencies = _identity(frame, "export_frequency", frequency)
            dataset_versions = _identity(frame, "dataset_version")
            _identity(frame, "data_contract")
            years = {int(str(value)[:4]) for value in frame.trading_day.unique()}
            if not years.issubset({2020, 2021, 2022}):
                raise ValueError(f"Development read crossed year boundary: {years}")
            state_series, diagnostics = build_state_series(
                frame,
                close_times=profile.close_times,
                t1=t1,
                t2=t2,
            )
            results.append({
                "carrier": carrier,
                "profile_id": profile_id,
                "bar_interval": frequency,
                "layer1_view_id": view_ids[0],
                "export_frequency": frequencies[0],
                "dataset_versions": dataset_versions,
                "input_rows": int(len(frame)),
                **diagnostics,
                **episode_adequacy(state_series),
            })

    return {
        "schema_id": "trend_m5_development_adequacy@1.0",
        "milestone": "M5-2",
        "scope": "Development episode-entry counts and future-bar availability only",
        "development_start": START,
        "development_end": END,
        "t1": t1,
        "primary_t2": t2,
        "results": results,
        "validation_rows_read": False,
        "holdout_rows_read": False,
        "survival_outcomes_computed": False,
        "reversal_outcomes_computed": False,
        "returns_computed": False,
        "transition_probabilities_computed": False,
        "mfe_mae_computed": False,
        "hypothesis_test_performed": False,
        "h1_adjudicated": False,
        "production_authority": False,
        "fresh_oos": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
