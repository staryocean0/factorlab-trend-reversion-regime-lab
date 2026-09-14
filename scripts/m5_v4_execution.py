from __future__ import annotations

from pathlib import Path

from factor_lab.market_state.trend_regime_profiles import resolve_trend_profile
from regime_lab.market_data import load_market_data
from scripts.m5_development_adequacy_core import build_state_series
from scripts.m5_primary_validation_core import analyze_profile
from scripts.m5_validation_bootstrap import holm_adjust
from scripts.m5_validation_durations import duration_summaries
from scripts.m5_validation_transitions import transition_summaries

CARRIER = "000852.SH"
CONTEXT_START = "2022-12-30"
PROFILES = {"trend_1m_official_v1": "1m", "trend_5m_offset0_v1": "5m"}
PLANNED = (("1m", "UP"), ("1m", "DOWN"), ("5m", "UP"), ("5m", "DOWN"), ("15m", "UP"), ("15m", "DOWN"), ("60m", "UP"), ("60m", "DOWN"))


def _identity(frame, column: str, expected: str | None = None):
    if column not in frame.columns or frame[column].dropna().empty:
        raise ValueError(f"missing identity column: {column}")
    values = sorted({str(value) for value in frame[column].dropna().unique()})
    if expected is not None and values != [expected]:
        raise ValueError(f"{column} drift")
    return values


def secondary_rule(block):
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


def execute_validation(root: Path, protocol: dict):
    validation_start = protocol["sample_calendar"]["validation"]["start"]
    validation_end = protocol["sample_calendar"]["validation"]["end"]
    if (validation_start, validation_end) != ("2023-01-03", "2024-12-31"):
        raise ValueError("Validation split drift")
    t1 = float(protocol["state_scheme"]["t1"])
    t2 = float(protocol["state_scheme"]["primary_t2"])
    if (t1, t2) != (2.0, 4.0):
        raise ValueError("primary threshold drift")

    profile_results = {}
    for profile_id, frequency in PROFILES.items():
        profile = resolve_trend_profile(bar_interval=frequency, profile_id=profile_id)
        frame = load_market_data(CARRIER, frequency, CONTEXT_START, validation_end, root=root)
        _identity(frame, "export_view_id", profile.layer1_view_id)
        _identity(frame, "export_frequency", frequency)
        dataset_versions = _identity(frame, "dataset_version")
        _identity(frame, "data_contract")
        years = {int(str(value)[:4]) for value in frame.trading_day.unique()}
        if not years.issubset({2022, 2023, 2024}) or 2025 in years:
            raise ValueError(f"Validation read crossed frozen boundary: {years}")
        states, diagnostics = build_state_series(frame, close_times=profile.close_times, t1=t1, t2=t2)
        metrics = analyze_profile(frame, states, validation_start=validation_start, validation_end=validation_end)
        metrics.update(transition_summaries(frame, states, validation_start=validation_start, validation_end=validation_end))
        metrics["descriptive"].update(duration_summaries(frame, states, validation_start=validation_start, validation_end=validation_end))
        profile_results[frequency] = {
            "profile_id": profile_id,
            "layer1_view_id": profile.layer1_view_id,
            "dataset_versions": dataset_versions,
            "input_rows_with_context": int(len(frame)),
            "diagnostics": diagnostics,
            **metrics,
        }

    planned = []
    raw_p = []
    for interval, direction in PLANNED:
        if interval not in profile_results:
            planned.append({"interval": interval, "direction": direction, "status": "NOT_ADMITTED", "raw_p": 1.0})
            raw_p.append(1.0)
            continue
        block = profile_results[interval]["primary_and_confirmatory"][direction]
        primary = block["primary_survival_5"]
        p_value = float(primary["one_sided_bootstrap_p"]) if block["primary_adequate"] and primary else 1.0
        planned.append({"interval": interval, "direction": direction, "status": "PENDING_HOLM", "raw_p": p_value})
        raw_p.append(p_value)

    adjusted = holm_adjust(raw_p)
    for item, adjusted_p in zip(planned, adjusted, strict=True):
        item["holm_adjusted_p"] = adjusted_p
        if item["status"] == "NOT_ADMITTED":
            continue
        block = profile_results[item["interval"]]["primary_and_confirmatory"][item["direction"]]
        primary = block["primary_survival_5"]
        secondary = secondary_rule(block)
        item["secondary_rule"] = secondary
        item["primary_adequate"] = block["primary_adequate"]
        item["primary_contrast"] = None if primary is None else primary["strong_minus_moderate"]
        item["primary_ci95"] = None if primary is None else primary["ci95"]
        if not block["primary_adequate"] or primary is None:
            item["status"] = "INCONCLUSIVE_UNDERPOWERED"
        elif adjusted_p <= 0.05 and primary["strong_minus_moderate"] <= -0.05 and secondary["passes"]:
            item["status"] = "VALIDATION_SUPPORT"
        elif primary["ci95"][0] > 0.0:
            item["status"] = "H1_CONTRADICTED"
        else:
            item["status"] = "H1_NOT_SUPPORTED"

    return {
        "schema_id": "trend_m5_primary_validation@1.0",
        "milestone": "M5-4",
        "carrier": CARRIER,
        "primary_t2": t2,
        "validation": {"start": validation_start, "end": validation_end, "context_start": CONTEXT_START},
        "profile_results": profile_results,
        "planned_primary_family": planned,
        "supporting_contrasts": [f"{x['interval']}:{x['direction']}" for x in planned if x["status"] == "VALIDATION_SUPPORT"],
        "validation_rows_read": True,
        "holdout_rows_read": False,
        "holdout_unlocked": False,
        "sensitivity_t2_3_5_run": False,
        "replication_000688_run": False,
        "protocol_changed": False,
        "production_authority": False,
        "fresh_oos": False,
        "next_allowed_step": "M5-5 predeclared T2=3/5 validation sensitivity; holdout remains locked",
    }
