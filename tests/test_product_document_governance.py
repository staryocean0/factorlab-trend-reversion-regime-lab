"""Regression coverage for milestone product-document governance."""

import json
from pathlib import Path

from scripts.repository_consistency import lifecycle, status_only_text

ROOT = Path(__file__).resolve().parents[1]


def state():
    return {
        "scientific_status": "DONE",
        "BLACKBOX_query_count": 3,
        "production_authority": False,
        "fresh_oos": False,
        "latest_review": "docs/research/review.md",
        "generated_documents": {"README.md": "# README"},
        "manual_workflows": [],
        "modules": {},
    }


def test_status_only_render_preserves_product_body():
    body = """# Product

<!-- GENERATED: edit docs/REPOSITORY_STATE.json, then --render -->
> stale
<!-- END GENERATED STATUS -->

## Milestone
Keep this body.
"""
    rendered = status_only_text("README.md", body, state())
    assert "Keep this body." in rendered
    assert "> 机器状态：`DONE`。" in rendered
    assert "> stale" not in rendered


def test_current_product_docs_have_explicit_lifecycle():
    s = state()
    for path in (
        "CHANGELOG.md",
        "docs/ROADMAP.md",
        "docs/API_CONTRACT.md",
        "docs/API_EXAMPLES.md",
        "docs/API_GAP_ANALYSIS.md",
        "docs/RELEASE.md",
        "docs/THREE_BUCKET_BASELINE.md",
    ):
        assert lifecycle(path, s) == "CURRENT_PRODUCT_DOCUMENTATION"


def test_m9_component_release_governance_is_fail_closed_and_non_production():
    contract = json.loads(
        (ROOT / "docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json").read_text(encoding="utf-8")
    )

    assert contract["schema_id"] == "trend_m9_release_governance@1.0"
    assert contract["status"] == "PASS_STABLE_COMPONENT_V1_RELEASE_GOVERNANCE"
    assert contract["component_release_version"] == "1.0.0"
    assert contract["canonical_git_tag"] == "trend-regime-v1.0.0"
    assert contract["release_pointer_branch"] == "release/trend-regime-v1.0.0"
    assert contract["roadmap_complete"] is True
    assert contract["automatic_next_milestone"] is None

    surface = contract["stable_public_surface"]
    assert surface["call"] == "query_regime(symbol, as_of, bar_interval, profile_id=None)"
    assert surface["state_enum"] == ["DOWN", "SIDEWAYS", "UP"]
    assert surface["strength"] == "abs(directional_score)"

    assert contract["current_runtime_admission"]["profiles"] == [
        "trend_1m_official_v1",
        "trend_5m_offset0_v1",
    ]
    assert len(contract["current_runtime_admission"]["not_admitted_in_v1"]) == 8
    assert contract["python_distribution"]["is_component_semver_authority"] is False
    assert contract["python_distribution"]["repository_pyproject_version"] == "0.1.0"

    major = "\n".join(contract["compatibility_policy"]["major_release_required"])
    for phrase in (
        "state enum or T1",
        "estimator or directional_score",
        "strength definition",
        "snapshot identity or expiry/no-fallback",
        "formal T2",
        "Layer2 global_state",
        "production_authority=false",
    ):
        assert phrase in major

    assert [row["milestone"] for row in contract["evidence_lineage"]] == [
        "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"
    ]
    for row in contract["evidence_lineage"]:
        assert (ROOT / row["authority"]).is_file()

    assert contract["market_outcomes_computed"] is False
    assert contract["m5_outcome_reopened"] is False
    assert contract["holdout_read"] is False
    assert contract["fresh_oos"] is False
    assert contract["production_authority"] is False
    assert contract["trading_action_authority"] is False

    for relative in contract["release_artifacts"]:
        assert (ROOT / relative).is_file()

    release = (ROOT / "docs/governance/TREND_V1_RELEASE.md").read_text(encoding="utf-8")
    assert "production_authority=false" in release
    assert "fresh_oos=false" in release
    assert "STATE_NOT_ADMITTED" in release
    assert "trend-regime-v1.0.0" in release


def test_post_v1_cross_profile_research_is_fail_closed_and_does_not_mutate_v1():
    gov = ROOT / "docs/governance"
    protocol = json.loads((gov / "TREND_CROSS_PROFILE_INVARIANCE_PROTOCOL_V1.json").read_text(encoding="utf-8"))
    inventory = json.loads((gov / "TREND_CROSS_PROFILE_SOURCE_INVENTORY_V1.json").read_text(encoding="utf-8"))
    freeze = json.loads((gov / "TREND_X2_DISTRIBUTIONAL_INVARIANCE_FREEZE_V1.json").read_text(encoding="utf-8"))
    result = json.loads((gov / "TREND_X2_DISTRIBUTIONAL_INVARIANCE_RESULT_V1.json").read_text(encoding="utf-8"))
    sensitivity = json.loads((gov / "TREND_X2_DIAGNOSTIC_SENSITIVITY_RESULT_V1.json").read_text(encoding="utf-8"))
    x3_freeze = json.loads((gov / "TREND_X3_STATE_DYNAMICS_INVARIANCE_FREEZE_V1.json").read_text(encoding="utf-8"))
    x3_result = json.loads((gov / "TREND_X3_STATE_DYNAMICS_INVARIANCE_RESULT_V1.json").read_text(encoding="utf-8"))
    x4 = json.loads((gov / "TREND_X4_CALIBRATION_FAMILY_DECISION_V1.json").read_text(encoding="utf-8"))
    x5 = json.loads((gov / "TREND_X5_CROSS_CARRIER_SOURCE_SEARCH_V1.json").read_text(encoding="utf-8"))

    assert protocol["status"] == "AUTHORIZED_PROTOCOL_FROZEN_BEFORE_MARKET_OUTCOMES"
    assert protocol["relationship_to_v1"]["v1_semantics_modified"] is False
    assert protocol["relationship_to_v1"]["runtime_admission_modified"] is False
    assert protocol["relationship_to_v1"]["v1_release_pointer_must_not_move_for_this_research"] is True

    assert inventory["status"] == "X1_COMPLETE_SOURCE_METADATA_INVENTORIED_NO_MARKET_OUTCOMES"
    assert inventory["market_data_rows_read"] is False
    assert inventory["runtime_admission_changed"] is False

    assert freeze["fixed_measurement"]["lookback_bars"] == 20
    assert freeze["fixed_measurement"]["t1"] == 2.0
    assert freeze["research_window"]["old_m4_m5_2025_holdout_included"] is False

    assert result["status"] == "X2_FIXED_BASELINE_COMPLETE"
    assert result["market_outcomes_computed"] is False
    assert result["trading_return_metrics_computed"] is False
    assert result["parameter_tuning_performed"] is False
    assert result["runtime_admission_changed"] is False
    phase_max = max(row["max_occupancy_range"] for row in result["same_interval_phase_dispersion"])
    assert phase_max < 0.04
    by_view = {row["view_id"]: row for row in result["matched_profile_cross_carrier"]}
    assert by_view["60m_offset_30"]["max_occupancy_abs_diff"] > by_view["5m_offset_0"]["max_occupancy_abs_diff"]

    assert sensitivity["status"] == "COMPLETE_NO_PRODUCT_PARAMETER_SELECTION"
    assert sensitivity["lookback_grid"] == [10, 20, 40]
    assert sensitivity["t1_grid"] == [1.5, 2.0, 2.5]
    assert sensitivity["v1_parameter_changed"] is False
    assert sensitivity["runtime_admission_changed"] is False
    sens_by_interval = {row["interval"]: row["max_abs_diff"] for row in sensitivity["cross_carrier_max_mean_occupancy_difference_across_grid"]}
    assert sens_by_interval["60m"] > sens_by_interval["5m"]

    assert x3_freeze["status"] == "FROZEN_BEFORE_X3_STATISTICS"
    assert x3_freeze["fixed_measurement"]["lookback_bars"] == 20
    assert x3_freeze["fixed_measurement"]["t1"] == 2.0
    assert x3_freeze["research_window"]["old_m4_m5_2025_holdout_included"] is False
    assert x3_freeze["runtime_admission_change_forbidden"] is True

    assert x3_result["status"] == "X3_COMPLETE_INTERVAL_HETEROGENEITY_WITH_PHASE_STABILITY"
    assert x3_result["market_return_outcomes_computed"] is False
    assert x3_result["trading_return_metrics_computed"] is False
    assert x3_result["runtime_admission_changed"] is False
    assert x3_result["v1_parameter_changed"] is False
    x3_by_view = {(row["carrier"], row["view_id"]): row for row in x3_result["summary_by_profile"]}
    assert x3_by_view[("000852.SH", "60m_offset_30")]["support"]["UP"].startswith("UNDERPOWERED")
    assert x3_by_view[("000688.SH", "60m_offset_30")]["support"]["UP"].startswith("UNDERPOWERED")

    assert x4["status"] == "PASS_DECISION_INSUFFICIENT_EVIDENCE_NO_V1_CHANGE"
    assert x4["selected_decision"] == "INSUFFICIENT_EVIDENCE"
    assert all(value is False for value in x4["v1_effect"].values())
    assert x4["governance"]["old_m4_m5_2025_holdout_read"] is False
    assert x4["governance"]["m5_outcomes_reopened"] is False

    assert x5["status"] == "X5_STARTED_ADDITIONAL_EXACT_VIEW_SOURCES_NOT_YET_LOCATED"
    assert x5["minimum_generality_target"] == 5
    assert all(row["status"] == "SOURCE_NOT_LOCATED_IN_CURRENT_ACCESSIBLE_GITHUB_SCOPE" for row in x5["candidate_searches"])
    assert x5["v1_effect"]["runtime_admission_changed"] is False
    assert x5["v1_effect"]["release_pointer_changed"] is False

    for obj in (protocol["relationship_to_v1"], inventory, result, sensitivity, x3_result, x4["governance"], x5["governance"]):
        assert obj["production_authority"] is False
