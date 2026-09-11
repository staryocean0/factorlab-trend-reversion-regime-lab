from __future__ import annotations

from datetime import date
from pathlib import Path

from research.r1b_mo_pre_execution.selection import (
    CandidateContract,
    completed_net_cny,
    horizon_end_idx,
    select_contract,
)
from research.r1b_mo_pre_execution.validate_pre_execution_freeze import validate_freeze

REPO = Path(__file__).resolve().parents[1]


def _contracts() -> list[CandidateContract]:
    return [
        CandidateContract("MO2302-C-6400", "C", 6400.0, date(2023, 2, 17)),
        CandidateContract("MO2302-C-6600", "C", 6600.0, date(2023, 2, 17)),
        CandidateContract("MO2302-P-6400", "P", 6400.0, date(2023, 2, 17)),
        CandidateContract("MO2302-P-6600", "P", 6600.0, date(2023, 2, 17)),
        CandidateContract("MO2303-C-6500", "C", 6500.0, date(2023, 3, 17)),
    ]


def test_horizon_index_is_entry_plus_1200():
    assert horizon_end_idx(10, 1200) == 1210


def test_call_distance_tie_selects_otm_higher_strike():
    chosen = select_contract(_contracts(), spot=6500.0, option_type="C", horizon_date=date(2023, 1, 15))
    assert chosen is not None
    assert chosen.contract_code == "MO2302-C-6600"


def test_put_distance_tie_selects_otm_lower_strike():
    chosen = select_contract(_contracts(), spot=6500.0, option_type="P", horizon_date=date(2023, 1, 15))
    assert chosen is not None
    assert chosen.contract_code == "MO2302-P-6400"


def test_expiry_then_strike_prefers_nearest_covering_expiry():
    chosen = select_contract(_contracts(), spot=6500.0, option_type="C", horizon_date=date(2023, 1, 15))
    assert chosen is not None
    assert chosen.expiry == date(2023, 2, 17)


def test_no_covering_expiry_returns_none():
    chosen = select_contract(_contracts(), spot=6500.0, option_type="C", horizon_date=date(2023, 3, 17))
    assert chosen is None


def test_completed_net_uses_ask_entry_bid_exit_and_14_plus_14():
    assert completed_net_cny(10.0, 13.0, 14.0, 14.0, 100.0) == 272.0


def test_freeze_contract_mapping_stays_sealed_after_outcome_authorization():
    receipt = validate_freeze(REPO / "docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json", REPO)
    assert receipt.status == "PASS"
    assert receipt.empirical_option_outcome_test_authorized is True
    assert receipt.outcome_runner_authorized is True
    assert receipt.errors == []
