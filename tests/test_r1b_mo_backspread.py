from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from research.r1b_mo_backspread.run_study import adjudicate, first_joint_valid
from research.r1b_mo_backspread.selection import completed_backspread_net_cny, select_backspread_pair
from research.r1b_mo_outcome.quotes import MonthlyQuoteStore
from research.r1b_mo_pre_execution.selection import CandidateContract


def _c(code: str, typ: str, strike: float) -> CandidateContract:
    return CandidateContract(code, typ, strike, date(2026, 1, 16))


def test_selects_frozen_atm_and_single_adjacent_otm_call():
    pool = [_c("C4900", "C", 4900), _c("C5000", "C", 5000), _c("C5100", "C", 5100), _c("C5200", "C", 5200)]
    pair = select_backspread_pair(pool, 5000.0, "C", date(2025, 12, 31))
    assert pair is not None
    assert pair.short_atm.strike == 5000
    assert pair.long_otm.strike == 5100


def test_selects_frozen_atm_and_single_adjacent_otm_put():
    pool = [_c("P4800", "P", 4800), _c("P4900", "P", 4900), _c("P5000", "P", 5000), _c("P5100", "P", 5100)]
    pair = select_backspread_pair(pool, 5000.0, "P", date(2025, 12, 31))
    assert pair is not None
    assert pair.short_atm.strike == 5000
    assert pair.long_otm.strike == 4900


def test_backspread_net_charges_six_contract_legs():
    net = completed_backspread_net_cny(
        short_entry_bid=100.0,
        short_exit_ask=60.0,
        long_entry_ask=60.0,
        long_exit_bid=80.0,
        multiplier=100.0,
        fee_per_contract_per_leg=14.0,
    )
    assert net == (40.0 + 2 * 20.0) * 100 - 84


def _write_quote_pack(root: Path) -> MonthlyQuoteStore:
    quotes = root / "mo_quotes"
    quotes.mkdir()
    master = root / "contract_master.csv"
    pd.DataFrame(
        [
            {"contract_code": "MO2601-C-5000", "option_type": "C", "strike": 5000, "expiry": "2026-01-16"},
            {"contract_code": "MO2601-C-5100", "option_type": "C", "strike": 5100, "expiry": "2026-01-16"},
        ]
    ).to_csv(master, index=False)
    rows = [
        # asynchronous valid quotes at 09:31 must not be legged together
        {"contract_code": "MO2601-C-5000", "option_type": "C", "strike": 5000, "expiry": "2026-01-16", "timestamp": "2025-12-01 09:31:00", "bid1": 100, "bid1_size": 2, "ask1": 101, "ask1_size": 2, "trading_status": "TRADING"},
        {"contract_code": "MO2601-C-5100", "option_type": "C", "strike": 5100, "expiry": "2026-01-16", "timestamp": "2025-12-01 09:31:03", "bid1": 59, "bid1_size": 3, "ask1": 60, "ask1_size": 3, "trading_status": "TRADING"},
        # first common executable snapshot
        {"contract_code": "MO2601-C-5000", "option_type": "C", "strike": 5000, "expiry": "2026-01-16", "timestamp": "2025-12-01 09:31:06", "bid1": 99, "bid1_size": 2, "ask1": 100, "ask1_size": 2, "trading_status": "TRADING"},
        {"contract_code": "MO2601-C-5100", "option_type": "C", "strike": 5100, "expiry": "2026-01-16", "timestamp": "2025-12-01 09:31:06", "bid1": 58, "bid1_size": 3, "ask1": 59, "ask1_size": 3, "trading_status": "TRADING"},
    ]
    pd.DataFrame(rows).to_csv(quotes / "mo_2025-12.csv", index=False)
    return MonthlyQuoteStore(quotes, master_path=master)


def test_joint_execution_requires_same_timestamp_and_two_long_contracts(tmp_path: Path):
    store = _write_quote_pack(tmp_path)
    fill = first_joint_valid(
        store,
        short_code="MO2601-C-5000",
        long_code="MO2601-C-5100",
        start_ts=pd.Timestamp("2025-12-01 09:31:00", tz="Asia/Shanghai"),
        phase="entry",
    )
    assert fill is not None
    assert str(fill["timestamp"]) == "2025-12-01 09:31:06+08:00"
    assert fill["short_price"] == 99
    assert fill["long_price"] == 59


def test_adjudication_uses_precommitted_tail_strategy_gates():
    rows = []
    for year in (2023, 2024, 2025):
        for quarter in range(1, 5):
            month = 1 + (quarter - 1) * 3
            # all quarters positive; enough rows for stable simple fixture
            rows.append({"status": "completed_backspread", "entry_day": f"{year}-{month:02d}-05", "net_cny": 100.0})
    rows.extend([{"status": "joint_entry_unavailable", "entry_day": "2024-01-05", "net_cny": None}] * 2)
    ledger = pd.DataFrame(rows)
    freeze = {
        "viability_gates": {
            "joint_fill_coverage_min_fraction": 0.80,
            "annual_mean_net_positive_min_years": 2,
            "annual_mean_net_year_set": [2023, 2024, 2025],
            "quarterly_mean_net_positive_min_quarters": 6,
        }
    }
    result = adjudicate(ledger, freeze)
    assert result["passed"] is True
    assert result["decision"] == "PASS_RESEARCH_CANDIDATE_ACCOUNT_AUDIT_REQUIRED"
    assert result["annual_positive_years"] == 3
    assert result["quarterly_positive_quarters"] == 12
