import json
import subprocess
from pathlib import Path

import pytest

from factor_lab.market_state.trend_regime_representation import (
    REPRESENTATION_SCHEMA_ID,
    STATE_SCHEME_ID,
    STRENGTH_DEFINITION_ID,
    TrendRegimeRepresentation,
    represent_trend_state,
)

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/governance/TREND_M6_REPRESENTATION_DECISION_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_m6_selected_three_bucket_plus_continuous_strength():
    payload = json.loads(DECISION.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS_FROZEN_THREE_BUCKET_PLUS_CONTINUOUS_STRENGTH"
    assert payload["selected_option"] == "THREE_BUCKET_PLUS_CONTINUOUS_STRENGTH"
    assert payload["selected_representation_schema_id"] == REPRESENTATION_SCHEMA_ID
    assert payload["state_scheme_id"] == STATE_SCHEME_ID
    assert payload["state_enum"] == ["DOWN", "SIDEWAYS", "UP"]
    assert payload["continuous_strength"]["strength_definition_id"] == STRENGTH_DEFINITION_ID
    assert payload["t2_product_policy"]["formal_product_t2"] is None
    assert payload["t2_product_policy"]["caller_may_supply_t2"] is False
    assert payload["t2_product_policy"]["stable_consumer_may_emit_strong_state"] is False
    assert payload["formal_product_state_exclusions"] == ["STRONG_DOWN", "STRONG_UP"]


def test_m6_decision_preserves_m5_scope_and_does_not_reopen_outcomes():
    payload = json.loads(DECISION.read_text(encoding="utf-8"))
    assert payload["evidence_scope"]["empirically_supported_strength_intervals"] == ["1m", "5m"]
    assert payload["evidence_scope"]["not_empirically_certified_intervals"] == ["15m", "60m"]
    assert payload["evidence_scope"]["phase_profiles_empirically_certified"] is False
    assert payload["evidence_scope"]["fresh_oos"] is False
    assert payload["m5_outcome_reopen_allowed"] is False
    assert payload["holdout_read_allowed"] is False
    assert payload["next_allowed_step"] == "M7 stable consumer implementation only"


def test_m6_locked_objects_match():
    payload = json.loads(DECISION.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]


def test_representation_preserves_direction_and_strength_without_t2():
    down = represent_trend_state(state="DOWN", slope_t=-3.5)
    sideways_negative = represent_trend_state(state="SIDEWAYS", slope_t=-2.0)
    sideways_positive = represent_trend_state(state="SIDEWAYS", slope_t=2.0)
    up = represent_trend_state(state="UP", slope_t=4.25)

    assert down.directional_score == -3.5
    assert down.strength == 3.5
    assert sideways_negative.strength == 2.0
    assert sideways_positive.strength == 2.0
    assert up.directional_score == 4.25
    assert up.strength == 4.25

    payload = up.to_dict()
    assert payload["representation_schema_id"] == REPRESENTATION_SCHEMA_ID
    assert payload["state_scheme_id"] == STATE_SCHEME_ID
    assert payload["strength_definition_id"] == STRENGTH_DEFINITION_ID
    assert "t2" not in payload
    assert "strong_state" not in payload
    assert payload["production_authority"] is False
    assert payload["trading_action_authority"] is False


def test_representation_rejects_state_score_drift_and_authority_drift():
    with pytest.raises(ValueError, match="state is inconsistent"):
        represent_trend_state(state="UP", slope_t=1.0)
    with pytest.raises(ValueError, match="formal state"):
        represent_trend_state(state="STRONG_UP", slope_t=5.0)
    with pytest.raises(ValueError, match="strength must equal"):
        TrendRegimeRepresentation(state="UP", directional_score=3.0, strength=2.9)
    with pytest.raises(ValueError, match="production/trading authority"):
        TrendRegimeRepresentation(
            state="UP",
            directional_score=3.0,
            strength=3.0,
            trading_action_authority=True,
        )


def test_rejected_options_do_not_enter_v1_stable_api():
    payload = json.loads(DECISION.read_text(encoding="utf-8"))
    rejected = {item["option"]: item["decision"] for item in payload["rejected_options"]}
    assert rejected == {
        "FORMAL_FIVE_BUCKET": "REJECTED_FOR_V1",
        "THREE_BUCKET_PLUS_FIVE_BUCKET_DIAGNOSTIC_PRODUCT_EXTENSION": "REJECTED_FOR_V1_STABLE_API",
    }
    assert payload["research_artifact_policy"]["m4_m5_five_bucket_artifacts_retained"] is True
    assert payload["research_artifact_policy"]["may_be_returned_by_m7_stable_consumer"] is False
