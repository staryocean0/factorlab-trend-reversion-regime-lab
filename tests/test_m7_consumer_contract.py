import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs/governance/TREND_M7_CONSUMER_CONTRACT_V1.json"


def _git_blob(path: str) -> str:
    return subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()


def test_m7_contract_freezes_public_surface_and_authority():
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    assert payload["schema_id"] == "trend_m7_consumer_contract@1.0"
    assert payload["status"] == "PASS_STABLE_CONSUMER_V1"
    assert payload["consumer_schema_id"] == "regime_state_consumer_v1"
    assert payload["snapshot_schema_id"] == "trend_regime_snapshot@1.0"
    assert payload["formal_state"]["enum"] == ["DOWN", "SIDEWAYS", "UP"]
    assert payload["formal_state"]["strong_states_allowed"] is False
    assert payload["formal_state"]["global_multi_interval_state_allowed"] is False
    assert payload["authority"]["measurement"] is True
    assert payload["authority"]["snapshot_read"] is True
    for key in ("strategy_selection", "parameter_selection", "routing", "trading_action", "production"):
        assert payload["authority"][key] is False
    assert payload["production_authority"] is False
    assert payload["fresh_oos"] is False


def test_m7_provider_and_lifecycle_are_fail_closed():
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    provider = payload["current_provider_admission"]
    assert provider["symbols"] == ["000688.SH", "000852.SH"]
    assert provider["profiles"] == ["trend_1m_official_v1", "trend_5m_offset0_v1"]
    assert provider["registry_frozen_in_v1"] is True
    assert provider["constructor_expansion_allowed"] is False
    assert provider["m3_engineering_profiles_not_in_current_admission_return"] == "STATE_NOT_ADMITTED"
    lifecycle = payload["lifecycle"]
    assert lifecycle["snapshot_immutable"] is True
    assert lifecycle["append_only_ingest"] is True
    assert lifecycle["latest_expired_no_fallback"] is True
    assert lifecycle["latest_explicit_unavailable_no_fallback"] is True
    assert lifecycle["unavailable_snapshot_suppresses_state_and_strength"] is True


def test_m7_stable_api_forbids_research_and_strategy_semantics():
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    forbidden = set(payload["forbidden_stable_output_semantics"])
    assert {"T2", "STRONG_UP", "STRONG_DOWN", "five_bucket_state", "global_state"} <= forbidden
    assert {"BUY", "SELL", "position", "order", "strategy_selection", "routing"} <= forbidden
    assert "provider_admission" in payload["public_query"]["caller_forbidden"]
    assert "validity_policy" in payload["public_query"]["caller_forbidden"]
    assert payload["m5_outcome_reopen_allowed"] is False
    assert payload["holdout_read_allowed"] is False
    assert payload["next_allowed_step"].startswith("M8 ")


def test_m7_locked_objects_match_exactly():
    payload = json.loads(CONTRACT.read_text(encoding="utf-8"))
    for item in payload["locked_objects"]:
        assert _git_blob(item["path"]) == item["git_blob"], item["path"]
        if "sha256" in item:
            actual = hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest()
            assert actual == item["sha256"], item["path"]
