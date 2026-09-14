"""M5-5 preregistered T2=3/5 Validation sensitivity.

Sensitivity only: it cannot replace the consumed T2=4 headline and it never
unlocks holdout.  The same CSI1000 Validation split and admitted 1m/5m views
are used; no local resampling or carrier pooling is allowed.
"""
from __future__ import annotations

from pathlib import Path

from factor_lab.market_state.trend_regime_profiles import resolve_trend_profile
from regime_lab.market_data import load_market_data
from scripts.m5_development_adequacy_core import build_state_series
from scripts.m5_primary_validation_core import analyze_profile

CARRIER = "000852.SH"
CONTEXT_START = "2022-12-30"
PROFILES = {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
DIRECTIONS = ("UP", "DOWN")
SENSITIVITY_T2 = (3.0, 5.0)


def _identity(frame, column: str, expected: str | None = None):
    if column not in frame.columns or frame[column].dropna().empty:
        raise ValueError(f"missing identity column: {column}")
    values = sorted({str(value) for value in frame[column].dropna().unique()})
    if expected is not None and values != [expected]:
        raise ValueError(f"{column} drift: {values} != {[expected]}")
    return values


def sensitivity_label(block: dict) -> str:
    primary = block["primary_survival_5"]
    if not block["primary_adequate"] or primary is None:
        return "SENSITIVITY_INCONCLUSIVE_UNDERPOWERED"
    low, high = primary["ci95"]
    if low > 0.0:
        return "SENSITIVITY_H1_CONTRADICTED"
    if high < 0.0:
        return "SENSITIVITY_H1_DIRECTION"
    return "SENSITIVITY_MIXED_OR_NULL"


def _compact_direction(block: dict) -> dict:
    primary = block["primary_survival_5"]
    reversal = block["secondary_reversal_10"]
    ret5 = block["secondary_return_5"]
    return {
        "status": sensitivity_label(block),
        "primary_adequate": bool(block["primary_adequate"]),
        "survival5": primary,
        "reversal10": reversal,
        "direction_adjusted_return5": ret5,
        "reversal_adequate": bool(block["reversal_adequate"]),
        "return_adequate": bool(block["return_adequate"]),
    }


def execute_sensitivity(root: Path, protocol: dict, primary_receipt: dict) -> dict:
    validation_start = protocol["sample_calendar"]["validation"]["start"]
    validation_end = protocol["sample_calendar"]["validation"]["end"]
    if (validation_start, validation_end) != ("2023-01-03", "2024-12-31"):
        raise ValueError("Validation split drift")
    if tuple(float(x) for x in protocol["state_scheme"]["sensitivity_t2"]) != SENSITIVITY_T2:
        raise ValueError("sensitivity T2 drift")
    if primary_receipt["overall_conclusion"] != "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS":
        raise ValueError("consumed T2=4 headline drift")
    if primary_receipt["holdout_unlocked"] or primary_receipt["holdout_rows_read"]:
        raise ValueError("holdout must remain locked")

    t1 = float(protocol["state_scheme"]["t1"])
    all_results = {}
    for t2 in SENSITIVITY_T2:
        per_profile = {}
        for profile_id, frequency in PROFILES.items():
            profile = resolve_trend_profile(bar_interval=frequency, profile_id=profile_id)
            frame = load_market_data(CARRIER, frequency, CONTEXT_START, validation_end, root=root)
            _identity(frame, "export_view_id", profile.layer1_view_id)
            _identity(frame, "export_frequency", frequency)
            dataset_versions = _identity(frame, "dataset_version")
            _identity(frame, "data_contract")
            years = {int(str(value)[:4]) for value in frame.trading_day.unique()}
            if not years.issubset({2022, 2023, 2024}) or 2025 in years:
                raise ValueError(f"sensitivity read crossed frozen boundary: {years}")
            states, diagnostics = build_state_series(
                frame,
                close_times=profile.close_times,
                t1=t1,
                t2=t2,
            )
            metrics = analyze_profile(
                frame,
                states,
                validation_start=validation_start,
                validation_end=validation_end,
            )
            per_profile[frequency] = {
                "profile_id": profile_id,
                "layer1_view_id": profile.layer1_view_id,
                "dataset_versions": dataset_versions,
                "input_rows_with_context": int(len(frame)),
                "diagnostics": diagnostics,
                "episode_counts": metrics["episode_counts"],
                "directions": {
                    direction: _compact_direction(metrics["primary_and_confirmatory"][direction])
                    for direction in DIRECTIONS
                },
            }
        labels = [per_profile[i]["directions"][d]["status"] for i in ("1m", "5m") for d in DIRECTIONS]
        all_results[str(int(t2))] = {
            "t2": t2,
            "profiles": per_profile,
            "contradicted_count": labels.count("SENSITIVITY_H1_CONTRADICTED"),
            "h1_direction_count": labels.count("SENSITIVITY_H1_DIRECTION"),
            "mixed_or_underpowered_count": 4 - labels.count("SENSITIVITY_H1_CONTRADICTED") - labels.count("SENSITIVITY_H1_DIRECTION"),
        }

    return {
        "schema_id": "trend_m5_t2_sensitivity@1.0",
        "milestone": "M5-5",
        "role": "PREDECLARED_VALIDATION_SENSITIVITY_ONLY_NOT_PRIMARY",
        "carrier": CARRIER,
        "validation": {"start": validation_start, "end": validation_end, "context_start": CONTEXT_START},
        "primary_t2_headline": 4.0,
        "primary_headline_conclusion": primary_receipt["overall_conclusion"],
        "sensitivity_results": all_results,
        "multiplicity_role": "no_new_primary_family; sensitivity cannot replace or rescue T2=4 headline",
        "validation_rows_read": True,
        "holdout_rows_read": False,
        "holdout_unlocked": False,
        "primary_validation_rerun": False,
        "replication_000688_run": False,
        "protocol_changed": False,
        "production_authority": False,
        "fresh_oos": False,
        "next_allowed_step": "M5-6 report preregistered replication/remaining robustness only; Holdout remains blocked",
    }
