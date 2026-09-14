"""Regression coverage for milestone product-document governance."""

from scripts.repository_consistency import lifecycle, status_only_text


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
