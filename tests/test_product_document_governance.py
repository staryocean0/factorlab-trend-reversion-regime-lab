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
        "docs/ROADMAP.md",
        "docs/API_CONTRACT.md",
        "docs/API_GAP_ANALYSIS.md",
        "docs/THREE_BUCKET_BASELINE.md",
    ):
        assert lifecycle(path, s) == "CURRENT_PRODUCT_DOCUMENTATION"


def test_m9_component_release_governance_is_fail_closed_and_non_production():
    contract = json.loads(
        (ROOT / "docs/governance/TREND_M9_RELEASE_GOVERNANCE_V1.json").read_text(encoding="utf-8")
    )

    assert contract["schema_id"] == "trend_m9_release_governance@1.0"
    assert contract["component_release_version"] == "1.0.0"
    assert contract["git_tag"] == "trend-regime-v1.0.0"
    assert contract["stable_public_surface"]["state_enum"] == ["DOWN", "SIDEWAYS", "UP"]
    assert contract["current_runtime_admission"]["profiles"] == [
        "trend_1m_official_v1",
        "trend_5m_offset0_v1",
    ]
    assert contract["python_distribution"]["is_component_semver_authority"] is False
    assert contract["python_distribution"]["repository_pyproject_version"] == "0.1.0"
    assert contract["market_outcomes_computed"] is False
    assert contract["m5_outcome_reopened"] is False
    assert contract["holdout_read"] is False
    assert contract["fresh_oos"] is False
    assert contract["production_authority"] is False
    assert contract["trading_action_authority"] is False

    for relative in contract["release_artifacts"]:
        assert (ROOT / relative).is_file()

    release = (ROOT / "docs/RELEASE.md").read_text(encoding="utf-8")
    assert "production_authority=false" in release
    assert "fresh_oos=false" in release
    assert "STATE_NOT_ADMITTED" in release
    assert "trend-regime-v1.0.0" in release
