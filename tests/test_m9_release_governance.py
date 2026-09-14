import json
from pathlib import Path
import tomllib

from factor_lab.market_state.trend_regime_consumer import (
    CONSUMER_SCHEMA_ID,
    SNAPSHOT_SCHEMA_ID,
    current_provider_admission,
)
from factor_lab.market_state.trend_regime_representation import (
    REPRESENTATION_SCHEMA_ID,
    STATE_SCHEME_ID,
    STRENGTH_DEFINITION_ID,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json"


def load_contract() -> dict[str, object]:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))


def test_m9_component_release_identity_is_independent_from_repo_distribution_version():
    payload = load_contract()
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert payload["schema_id"] == "trend_m9_release_governance@1.0"
    assert payload["milestone"] == "M9"
    assert payload["status"] == "PASS_STABLE_COMPONENT_V1_RELEASE_GOVERNANCE"
    assert payload["component_id"] == "factorlab.layer2.trend_regime"
    assert payload["component_release_version"] == "1.0.0"
    assert payload["canonical_git_tag"] == "trend-regime-v1.0.0"
    assert payload["release_pointer_branch"] == "release/trend-regime-v1.0.0"
    assert payload["roadmap_complete"] is True
    assert payload["automatic_next_milestone"] is None

    distribution = payload["python_distribution"]
    assert distribution["is_component_semver_authority"] is False
    assert distribution["repository_pyproject_version"] == "0.1.0"
    assert pyproject["project"]["version"] == "0.1.0"


def test_m9_public_surface_matches_frozen_m6_m7_runtime_constants():
    payload = load_contract()
    surface = payload["stable_public_surface"]

    assert surface["call"] == "query_regime(symbol, as_of, bar_interval, profile_id=None)"
    assert surface["consumer_schema_id"] == CONSUMER_SCHEMA_ID
    assert surface["snapshot_schema_id"] == SNAPSHOT_SCHEMA_ID
    assert surface["representation_schema_id"] == REPRESENTATION_SCHEMA_ID
    assert surface["state_scheme_id"] == STATE_SCHEME_ID
    assert surface["strength_definition_id"] == STRENGTH_DEFINITION_ID
    assert surface["state_enum"] == ["DOWN", "SIDEWAYS", "UP"]
    assert surface["strength"] == "abs(directional_score)"


def test_m9_runtime_admission_matches_m7_registry_and_does_not_expand_profiles():
    payload = load_contract()
    admission = payload["current_runtime_admission"]
    registry = current_provider_admission()

    assert admission["provider_id"] == registry.provider_id
    assert admission["source_dataset_id"] == registry.source_dataset_id
    assert admission["admission_receipt_id"] == registry.admission_receipt_id
    assert tuple(admission["symbols"]) == registry.admitted_symbols
    assert tuple(admission["profiles"]) == registry.admitted_profiles
    assert tuple(admission["profiles"]) == (
        "trend_1m_official_v1",
        "trend_5m_offset0_v1",
    )
    assert len(admission["not_admitted_in_v1"]) == 8


def test_m9_semver_policy_requires_major_for_product_semantic_changes():
    payload = load_contract()
    policy = payload["compatibility_policy"]
    major = "\n".join(policy["major_release_required"])

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
    assert "historical V1 snapshots are never rewritten" in policy["schema_rule"]


def test_m9_evidence_lineage_is_complete_and_ordered_m2_through_m9():
    payload = load_contract()
    lineage = payload["evidence_lineage"]

    assert [row["milestone"] for row in lineage] == [
        "M2",
        "M3",
        "M4",
        "M5",
        "M6",
        "M7",
        "M8",
        "M9",
    ]
    for row in lineage:
        assert (ROOT / row["authority"]).is_file()


def test_m9_release_artifacts_and_known_limitations_are_explicit():
    payload = load_contract()

    for relative in payload["release_artifacts"]:
        assert (ROOT / relative).is_file()

    limitations = "\n".join(payload["known_limitations"])
    assert "15m 60m" in limitations
    assert "no proven connected external strategy caller" in limitations
    assert "not live deployment" in limitations
    assert "Holdout was not opened" in limitations
    assert "no BUY SELL position order routing strategy-selection or production authority" in limitations


def test_m9_release_gate_cannot_reopen_research_or_grant_authority():
    payload = load_contract()
    forbidden = "\n".join(payload["release_gate"]["forbidden"])

    assert "reopen M5 outcomes" in forbidden
    assert "read the 2025 Holdout" in forbidden
    assert "expand runtime admission" in forbidden
    assert "map state or strength directly to a trading action" in forbidden
    assert "claim live or production integration" in forbidden
    assert "claim fresh OOS certification" in forbidden

    assert payload["market_outcomes_computed"] is False
    assert payload["m5_outcome_reopened"] is False
    assert payload["holdout_read"] is False
    assert payload["fresh_oos"] is False
    assert payload["production_authority"] is False
    assert payload["trading_action_authority"] is False


def test_m9_human_release_docs_preserve_non_strategy_boundary():
    release = (ROOT / "docs/RELEASE.md").read_text(encoding="utf-8")
    examples = (ROOT / "docs/API_EXAMPLES.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    assert "trend-regime-v1.0.0" in release
    assert "production_authority=false" in release
    assert "fresh_oos=false" in release
    assert "STATE_NOT_ADMITTED" in release
    assert "不是交易策略" in release

    assert "fused_state" in examples
    assert "selected_strategy" in examples
    assert "Layer 2 不投票" in examples
    assert "STATE_NOT_ADMITTED" in examples

    assert "[1.0.0] - 2026-09-14" in changelog
    assert "No BUY/SELL" in changelog
    assert "pyproject.toml` remains `0.1.0" in changelog
