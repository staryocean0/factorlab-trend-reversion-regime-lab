"""M5-6 preregistered STAR50 cross-carrier replication.

Replication is reported separately from the CSI1000 primary result. It cannot
rescue or replace the primary headline and it never unlocks the 2025 holdout.
"""
from __future__ import annotations

from pathlib import Path

from factor_lab.market_state.trend_regime_profiles import resolve_trend_profile
from regime_lab.market_data import load_market_data
from scripts.m5_development_adequacy_core import build_state_series
from scripts.m5_primary_validation_core import analyze_profile

CARRIER = "000688.SH"
CONTEXT_START = "2022-12-30"
PROFILES = {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
DIRECTIONS = ("UP", "DOWN")


def _identity(frame, column: str, expected: str | None = None):
    if column not in frame.columns or frame[column].dropna().empty:
        raise ValueError(f"missing identity column: {column}")
    values = sorted({str(value) for value in frame[column].dropna().unique()})
    if expected is not None and values != [expected]:
        raise ValueError(f"{column} drift: {values} != {[expected]}")
    return values


def replication_label(block: dict) -> str:
    primary = block["primary_survival_5"]
    if not block["primary_adequate"] or primary is None:
        return "REPLICATION_INCONCLUSIVE_UNDERPOWERED"
    low, high = primary["ci95"]
    if low > 0.0:
        return "REPLICATION_H1_CONTRADICTED"
    if high < 0.0:
        return "REPLICATION_H1_DIRECTION"
    return "REPLICATION_MIXED_OR_NULL"


def _compact(block: dict) -> dict:
    return {
        "status": replication_label(block),
        "primary_adequate": bool(block["primary_adequate"]),
        "survival5": block["primary_survival_5"],
        "reversal10": block["secondary_reversal_10"],
        "direction_adjusted_return5": block["secondary_return_5"],
        "reversal_adequate": bool(block["reversal_adequate"]),
        "return_adequate": bool(block["return_adequate"]),
    }


def execute_replication(root: Path, protocol: dict, primary_receipt: dict, sensitivity_receipt: dict) -> dict:
    validation_start = protocol["sample_calendar"]["validation"]["start"]
    validation_end = protocol["sample_calendar"]["validation"]["end"]
    if (validation_start, validation_end) != ("2023-01-03", "2024-12-31"):
        raise ValueError("Validation split drift")
    t1 = float(protocol["state_scheme"]["t1"])
    t2 = float(protocol["state_scheme"]["primary_t2"])
    if (t1, t2) != (2.0, 4.0):
        raise ValueError("primary threshold drift")
    if primary_receipt["overall_conclusion"] != "H1_CONTRADICTED_ON_ALL_EXECUTABLE_PRIMARY_CONTRASTS":
        raise ValueError("CSI1000 headline drift")
    if sensitivity_receipt["overall_sensitivity_conclusion"] != "T2_3_AND_T2_5_ALL_EXECUTABLE_CONTRASTS_H1_CONTRADICTED":
        raise ValueError("sensitivity receipt drift")
    if primary_receipt["holdout_unlocked"] or primary_receipt["holdout_rows_read"]:
        raise ValueError("holdout must remain locked")

    profiles = {}
    statuses = []
    point_same = 0
    clear_same = 0
    clear_opposite = 0
    for profile_id, frequency in PROFILES.items():
        profile = resolve_trend_profile(bar_interval=frequency, profile_id=profile_id)
        frame = load_market_data(CARRIER, frequency, CONTEXT_START, validation_end, root=root)
        _identity(frame, "export_view_id", profile.layer1_view_id)
        _identity(frame, "export_frequency", frequency)
        versions = _identity(frame, "dataset_version")
        _identity(frame, "data_contract")
        years = {int(str(value)[:4]) for value in frame.trading_day.unique()}
        if not years.issubset({2022, 2023, 2024}) or 2025 in years:
            raise ValueError(f"replication read crossed frozen boundary: {years}")
        states, diagnostics = build_state_series(frame, close_times=profile.close_times, t1=t1, t2=t2)
        metrics = analyze_profile(frame, states, validation_start=validation_start, validation_end=validation_end)
        directions = {}
        for direction in DIRECTIONS:
            block = metrics["primary_and_confirmatory"][direction]
            compact = _compact(block)
            directions[direction] = compact
            statuses.append(compact["status"])
            primary = compact["survival5"]
            if primary is not None:
                contrast = float(primary["strong_minus_moderate"])
                low, high = primary["ci95"]
                point_same += int(contrast > 0.0)
                clear_same += int(low > 0.0)
                clear_opposite += int(high < 0.0)
        profiles[frequency] = {
            "profile_id": profile_id,
            "layer1_view_id": profile.layer1_view_id,
            "dataset_versions": versions,
            "input_rows_with_context": int(len(frame)),
            "diagnostics": diagnostics,
            "episode_counts": metrics["episode_counts"],
            "directions": directions,
        }

    if clear_same == 4:
        replication_status = "CLEAR_QUALITATIVE_REPLICATION_OF_PRIMARY_CONTRADICTION"
    elif point_same == 4 and clear_opposite == 0:
        replication_status = "QUALITATIVE_REPLICATION_CONSISTENT_BUT_NOT_ALL_CLEAR"
    elif clear_opposite > 0:
        replication_status = "CROSS_CARRIER_INCONSISTENCY_PRESENT"
    else:
        replication_status = "CROSS_CARRIER_REPLICATION_MIXED_OR_INCONCLUSIVE"

    return {
        "schema_id": "trend_m5_star50_replication@1.0",
        "milestone": "M5-6",
        "role": "CROSS_CARRIER_REPLICATION_ONLY_NOT_PRIMARY_NOT_POOLED",
        "carrier": CARRIER,
        "validation": {"start": validation_start, "end": validation_end, "context_start": CONTEXT_START},
        "t1": t1,
        "t2": t2,
        "csi1000_primary_headline": primary_receipt["overall_conclusion"],
        "profiles": profiles,
        "replication_summary": {
            "status": replication_status,
            "executable_contrasts": 4,
            "point_estimate_same_direction_count": point_same,
            "statistically_clear_same_direction_count": clear_same,
            "statistically_clear_opposite_direction_count": clear_opposite,
            "h1_contradicted_label_count": statuses.count("REPLICATION_H1_CONTRADICTED"),
            "h1_direction_label_count": statuses.count("REPLICATION_H1_DIRECTION"),
        },
        "phase_sensitivity_reporting": {
            "status": "NOT_EXECUTABLE_NOT_ADMITTED",
            "profiles": ["trend_5m_offset1_v1", "trend_5m_offset2_v1", "trend_5m_offset3_v1", "trend_5m_offset4_v1", "trend_15m_offset10_v1", "trend_60m_offset45_v1"],
            "local_resampling_used": False,
            "profile_substitution_used": False,
        },
        "pooling_with_csi1000": False,
        "new_primary_family_created": False,
        "primary_headline_changed": False,
        "holdout_rows_read": False,
        "holdout_unlocked": False,
        "protocol_changed": False,
        "production_authority": False,
        "fresh_oos": False,
        "next_allowed_step": "M5 closeout only; then M6 representation decision in a later milestone",
    }
