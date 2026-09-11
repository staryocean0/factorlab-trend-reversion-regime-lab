#!/usr/bin/env python3
"""Validate that the R1B MO pre-execution freeze is complete and still result-free."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

DEFAULT_FREEZE = Path("docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json")
FORBIDDEN_OUTCOME_GLOBS = (
    "output/**/*mo*pnl*",
    "output/**/*option*outcome*",
    "docs/ops/evidence/**/*mo*pnl*",
    "docs/ops/evidence/**/*option_outcome*",
)

REQUIRED_ROOT_KEYS = (
    "freeze_id",
    "candidate_id",
    "status",
    "empirical_option_outcome_test_authorized",
    "outcome_runner_authorized",
    "inherited_r1b_clock",
    "underlying_binding",
    "joinable_evaluation_window",
    "option_mapping",
    "primary_payoff",
    "viability_gates",
    "explicit_prohibitions",
    "next_legal_action",
)


@dataclass
class FreezeReceipt:
    validator_id: str
    status: str
    freeze_path: str
    errors: list[str]
    warnings: list[str]
    empirical_option_outcome_test_authorized: bool = False
    outcome_runner_authorized: bool = False
    blackbox_query_count: int = 3
    production_authority: bool = False


def _require(condition: bool, errors: list[str], message: str) -> None:
    if not condition:
        errors.append(message)


def validate_freeze(freeze_path: Path, repo_root: Path) -> FreezeReceipt:
    errors: list[str] = []
    warnings: list[str] = []
    payload = json.loads(freeze_path.read_text(encoding="utf-8"))
    missing = [key for key in REQUIRED_ROOT_KEYS if key not in payload]
    _require(not missing, errors, f"freeze missing keys: {missing}")

    _require(payload.get("candidate_id") == "R1B_MO_ATM_DIRECTIONAL_LONG_SAME_CAUSAL_EXIT", errors, "candidate_id mismatch")
    allowed_status = {
        "FROZEN_RESULT_FREE",
        "OUTCOME_STUDY_AUTHORIZED",
        "OUTCOME_STUDY_EXECUTED",
        "OUTCOME_STUDY_FAIL_IDENTITY_CLOSED",
    }
    _require(payload.get("status") in allowed_status, errors, "status is not a legal freeze/outcome state")
    authorized = payload.get("empirical_option_outcome_test_authorized") is True
    runner_ok = payload.get("outcome_runner_authorized") is True
    if payload.get("status") == "FROZEN_RESULT_FREE":
        _require(authorized is False, errors, "outcome test must stay unauthorized while result-free")
        _require(runner_ok is False, errors, "outcome runner must stay unauthorized while result-free")
    else:
        _require(authorized, errors, "authorized outcome states must set empirical_option_outcome_test_authorized")
        _require(runner_ok, errors, "authorized outcome states must set outcome_runner_authorized")
    _require(payload.get("production_authority") is False, errors, "production_authority must be false")
    _require(payload.get("blackbox_query_4_authorized") is False, errors, "query #4 must stay closed")

    clock = payload.get("inherited_r1b_clock", {})
    _require(clock.get("horizon_bars") == 1200, errors, "horizon_bars must remain 1200")
    _require(clock.get("event_refit_forbidden") is True, errors, "event refit must stay forbidden")
    _require(abs(float(clock.get("S2_threshold", 0)) - 0.006891654009228464) < 1e-18, errors, "S2 threshold drift")
    _require(abs(float(clock.get("S3_threshold", 0)) - 0.013783308018456928) < 1e-18, errors, "S3 threshold drift")

    window = payload.get("joinable_evaluation_window", {})
    _require(window.get("start") == "2022-07-22", errors, "joinable start mismatch")
    _require(window.get("end") == "2025-12-31", errors, "joinable end must equal admitted underlying end")
    _require(window.get("fresh_oos") is False, errors, "fresh_oos must be false")
    _require(window.get("years_with_gate_vote") == ["2023", "2024", "2025"], errors, "gate-year set drift")

    mapping = payload.get("option_mapping", {})
    strike = mapping.get("strike_selection", {})
    _require("out-of-the-money" in str(strike.get("distance_tie", "")), errors, "ATM distance tie rule missing")
    _require(mapping.get("expiry_selection", {}).get("order") == "expiry_then_strike", errors, "expiry-then-strike order required")

    payoff = payload.get("primary_payoff", {})
    _require(payoff.get("open_fee_cny") == 14, errors, "open fee must be 14")
    _require(payoff.get("close_fee_cny") == 14, errors, "close fee must be 14")

    gates = payload.get("viability_gates", {})
    _require(gates.get("apply_only_after_separate_outcome_authorization") is True, errors, "gates must stay sealed")
    _require(gates.get("annual_mean_net_positive_min_years") == 2, errors, "annual gate drift")

    if not authorized:
        for pattern in FORBIDDEN_OUTCOME_GLOBS:
            hits = sorted(path for path in repo_root.glob(pattern) if path.is_file())
            if hits:
                errors.append(f"forbidden outcome artifact present: {[str(path) for path in hits[:5]]}")

    return FreezeReceipt(
        validator_id="rmr_R1B_MO_pre_execution_freeze_validator_v1",
        status="PASS" if not errors else "FAIL",
        freeze_path=str(freeze_path),
        errors=errors,
        warnings=warnings,
        empirical_option_outcome_test_authorized=authorized,
        outcome_runner_authorized=runner_ok,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the result-free R1B MO pre-execution freeze.")
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("docs/ops/evidence/r1b_mo_pre_execution_20260911/freeze_validator_receipt.json"),
    )
    args = parser.parse_args()
    receipt = validate_freeze(args.freeze, args.repo_root)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0 if receipt.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
