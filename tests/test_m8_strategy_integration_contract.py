"""Machine-contract guards for M8 strategy-layer integration validation."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/governance/TREND_M8_STRATEGY_INTEGRATION_V1.json"


def contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_m8_status_and_research_boundaries_are_frozen():
    doc = contract()
    assert doc["schema_id"] == "trend_m8_strategy_integration@1.0"
    assert doc["status"] == "PASS_INTEGRATION_BOUNDARIES_VALIDATED_WITH_EXPLICIT_STAR50_CALLER_GAP"
    assert doc["validation_mode"] == "synthetic_contract_integration_no_market_data"
    for key in (
        "production_authority",
        "fresh_oos",
        "market_outcomes_computed",
        "holdout_read",
        "m5_outcome_reopened",
        "external_repositories_modified",
        "m7_semantics_modified",
        "m6_representation_modified",
    ):
        assert doc[key] is False


def test_m7_identity_and_runtime_admission_are_unchanged():
    trend = contract()["trend_consumer"]
    assert trend["consumer_git_blob"] == "6ec31839a9497ad96fd59e9503c73ed1984569fa"
    assert trend["consumer_sha256"] == "5088c3a8e54348fa53d244ee52e64f520b0d0082a181d5c1142a90247d0468fc"
    assert trend["stable_fields"] == ["state", "directional_score", "strength"]
    assert trend["current_runtime_profiles"] == ["trend_1m_official_v1", "trend_5m_offset0_v1"]


def test_real_external_boundaries_are_pinned_without_overclaiming():
    boundaries = {row["id"]: row for row in contract()["external_boundaries"]}
    csi = boundaries["CSI1000_LAYER3_CALLER_BOUNDARY"]
    assert csi["repository"] == "staryocean0/csi1000-timing-strategy-private"
    assert csi["read_only_adapter"]["git_blob"] == "f8c2b37c84768fa5eac7529a3375015cf65d306b"
    assert csi["read_only_adapter"]["contract"] == {
        "read_only": True,
        "value_transformation": False,
        "thresholds": False,
        "strategy_mutation": False,
        "production_authority": False,
    }
    assert csi["layer3_orchestration"]["git_blob"] == "d0ea7e21b3a9cd18e42d6397b020c96c9dce1565"
    assert csi["layer3_orchestration"]["position_output"] is False

    star = boundaries["STAR50_PARALLEL_RISK_BOUNDARY"]
    assert star["repository"] == "staryocean0/factorlab-star50-filter-lab"
    assert star["role"] == "REAL_PARALLEL_LAYER2_RISK_PROVIDER_NOT_CLAIMED_AS_STRATEGY_CALLER"
    assert star["risk_consumer"]["git_blob"] == "b8454ee2a3970c1349496c2bf3997ff0cd209f23"
    assert star["example_boundary"]["git_blob"] == "27127d47660510b9214016b48a8ff94aab6811a4"
    assert star["example_boundary"]["actual_external_consumer_connected"] is False


def test_layer_ownership_and_fail_closed_semantics_are_frozen():
    rules = contract()["integration_invariants"]
    required_true = {
        "trend_layer2_read_only",
        "risk_and_trend_namespaces_separate",
        "multi_interval_trend_states_remain_separate",
        "layer2_global_state_forbidden",
        "direct_layer2_state_to_trade_action_forbidden",
        "unavailable_or_expired_must_not_become_sideways",
        "caller_threshold_mutation_forbidden",
        "caller_value_transformation_forbidden_at_layer2_adapter",
        "local_resampling_forbidden",
        "profile_substitution_forbidden",
        "layer3_owns_composition_conflict_and_selection",
        "final_action_mapping_remains_above_layer2",
    }
    assert required_true == {key for key, value in rules.items() if value is True}


def test_scope_limitations_and_next_step_are_explicit():
    doc = contract()
    scope = doc["scope_limitations"]
    assert scope["deployed_external_wiring_created"] is False
    assert scope["star50_external_strategy_caller_found"] is False
    assert scope["no_claim_of_live_or_production_integration"] is True
    assert scope["current_runtime_admission_unchanged"] is True
    assert doc["next_allowed_step"] == "M9 release versioning documentation and governance only"
