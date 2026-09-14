"""Govern the M5-1 source/profile admission receipt without computing outcomes."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M4 = ROOT / "docs/governance/TREND_FIVE_BUCKET_PROTOCOL_M4_V1.json"
M5 = ROOT / "docs/governance/TREND_M5_SOURCE_PROFILE_ADMISSION_V1.json"


def load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_m5_admission_is_metadata_only_and_keeps_outcomes_locked():
    receipt = load(M5)
    assert receipt["schema_id"] == "trend_m5_source_profile_admission@1.0"
    assert receipt["milestone"] == "M5-1"
    assert receipt["admission_only"] is True
    assert receipt["outcomes_computed"] is False
    assert receipt["five_bucket_episode_counts_computed"] is False
    assert receipt["forward_metrics_computed"] is False
    assert receipt["validation_outcomes_read"] is False
    assert receipt["holdout_outcomes_read"] is False
    assert receipt["production_authority"] is False
    assert receipt["fresh_oos"] is False
    assert receipt["local_resampling_used"] is False
    assert receipt["profile_substitution_used"] is False


def test_m5_anchor_receipt_covers_every_frozen_m4_anchor_for_both_carriers():
    protocol = load(M4)
    receipt = load(M5)
    anchors = protocol["profiles"]["anchors"]
    carriers = [
        protocol["carriers"]["primary"],
        *protocol["carriers"]["replication"],
    ]
    rows = receipt["anchor_admission"]
    assert len(rows) == len(anchors) * len(carriers) == 8
    assert {(row["carrier"], row["profile_id"]) for row in rows} == {
        (carrier, profile) for carrier in carriers for profile in anchors
    }
    assert all(row["status"] in {"ADMITTED", "NOT_ADMITTED"} for row in rows)


def test_only_current_exact_1m_and_5m_anchor_views_are_admitted():
    receipt = load(M5)
    admitted = [row for row in receipt["anchor_admission"] if row["status"] == "ADMITTED"]
    assert {(row["carrier"], row["profile_id"]) for row in admitted} == {
        ("000852.SH", "trend_1m_official_v1"),
        ("000852.SH", "trend_5m_offset0_v1"),
        ("000688.SH", "trend_1m_official_v1"),
        ("000688.SH", "trend_5m_offset0_v1"),
    }
    assert all(row["protocol_window_covered"] is True for row in admitted)
    assert {row["layer1_view_id"] for row in admitted} == {"1m_official", "5m_offset_0"}


def test_not_admitted_anchors_fail_closed_without_resampling_or_substitution():
    receipt = load(M5)
    blocked = [row for row in receipt["anchor_admission"] if row["status"] == "NOT_ADMITTED"]
    assert len(blocked) == 4
    assert {row["profile_id"] for row in blocked} == {
        "trend_15m_offset5_v1",
        "trend_60m_offset30_v1",
    }
    assert all(row["protocol_window_covered"] is False for row in blocked)
    assert all(row["local_resampling_forbidden"] is True for row in blocked)
    assert all(row["substitution_forbidden"] is True for row in blocked)
    assert all(row.get("reason_code") for row in blocked)


def test_phase_sensitivity_stays_unadmitted_until_exact_current_receipts_exist():
    protocol = load(M4)
    receipt = load(M5)
    rows = receipt["phase_sensitivity_admission"]
    assert {row["profile_id"] for row in rows} == set(protocol["profiles"]["phase_sensitivity"])
    assert all(row["status"] == "NOT_ADMITTED" for row in rows)
    assert all(row.get("reason_code") for row in rows)


def test_clock_adapter_does_not_misuse_historical_retrieval_available_at():
    receipt = load(M5)
    clock = receipt["clock_adapter_contract"]
    assert clock["historical_available_at_field_role"] == "historical_data_retrieval_availability_time_only"
    assert clock["m5_runtime_available_at"] == "bar_end"
    assert clock["measured_feed_latency_claimed"] is False
    assert clock["raw_historical_available_at_must_be_preserved_as_provenance"] is True


def test_next_step_is_development_only_and_keeps_validation_locked():
    receipt = load(M5)
    next_step = receipt["next_allowed_step"]
    assert next_step["milestone"] == "M5-2"
    assert "development" in next_step["scope"].lower()
    assert next_step["validation_outcomes_still_locked"] is True
    assert next_step["holdout_outcomes_still_locked"] is True
    assert next_step["protocol_change_allowed"] is False
    summary = receipt["m5_primary_anchor_summary"]
    assert summary["planned_anchor_carrier_pairs"] == 8
    assert summary["admitted_anchor_carrier_pairs"] == 4
    assert summary["not_admitted_anchor_carrier_pairs"] == 4
    assert summary["admitted_primary_intervals"] == ["1m", "5m"]
    assert summary["not_admitted_primary_intervals"] == ["15m", "60m"]
