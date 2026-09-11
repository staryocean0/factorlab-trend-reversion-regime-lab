from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from research.r1b_mo_outcome.adjudicate import adjudicate
from research.r1b_mo_outcome.events import UnderlyingEvent, temporal_exit
from research.r1b_mo_outcome.quotes import MonthlyQuoteStore
from research.r1b_mo_outcome.run_outcome_study import join_event
from research.r1b_mo_pre_execution.selection import completed_net_cny


def test_temporal_exit_failure_beats_later_completion():
    prices = np.array([100.0, 100.0, 99.8, 98.0, 101.0, 102.0])
    klass, idx = temporal_exit(prices, entry_idx=1, horizon_end_idx=5, parent_sign=1, failure=99.0, completion_idx=4)
    assert klass == "parent_failure"
    assert idx == 3


def test_temporal_exit_uses_confirm_index_not_an_earlier_extreme():
    prices = np.array([100.0, 100.2, 100.4, 103.0, 101.5, 101.2])
    klass, idx = temporal_exit(prices, entry_idx=1, horizon_end_idx=5, parent_sign=1, failure=90.0, completion_idx=5)
    assert klass == "temporal_completion"
    assert idx == 5
    assert idx != 3


def test_temporal_exit_censored_at_horizon_when_neither_hits():
    prices = np.array([100.0, 100.1, 100.2, 100.3, 100.4])
    klass, idx = temporal_exit(prices, entry_idx=1, horizon_end_idx=3, parent_sign=1, failure=90.0, completion_idx=None)
    assert klass == "censored"
    assert idx == 3


def test_quote_store_reads_daily_shards_and_contract_master(tmp_path: Path):
    quotes = tmp_path / "mo_quotes"
    quotes.mkdir()
    (quotes / "mo_2023-01-04.csv").write_text(
        "contract_code,option_type,strike,expiry,timestamp,bid1,bid1_size,ask1,ask1_size,trading_status\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 09:31:00.000000,10.0,1,10.4,2,TRADING\n",
        encoding="utf-8",
    )
    (quotes / "mo_2023-01-05.csv").write_text(
        "contract_code,option_type,strike,expiry,timestamp,bid1,bid1_size,ask1,ask1_size,trading_status\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-05 09:31:00.000000,10.2,1,10.6,2,TRADING\n",
        encoding="utf-8",
    )
    (tmp_path / "contract_master.csv").write_text(
        "contract_code,option_type,strike,expiry\nMO2302-C-6500,C,6500.0,2023-02-17\n",
        encoding="utf-8",
    )
    store = MonthlyQuoteStore(quotes)
    assert store.available_months == ["2023-01"]
    month = store.load_month("2023-01")
    assert len(month) == 2
    assert store.contract_master()[0].contract_code == "MO2302-C-6500"


def test_first_valid_ask_skips_nontrading_and_zero_size(tmp_path: Path):
    month = tmp_path / "mo_2023-01.csv"
    month.write_text(
        "contract_code,option_type,strike,expiry,timestamp,bid1,bid1_size,ask1,ask1_size,trading_status\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 09:31:00.000000,10.0,1,10.4,0,TRADING\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 09:31:03.000000,10.0,1,10.5,2,AUCTION_OR_NONCONTINUOUS\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 09:31:06.000000,10.1,1,10.6,3,TRADING\n",
        encoding="utf-8",
    )
    store = MonthlyQuoteStore(tmp_path)
    fill = store.first_valid("MO2302-C-6500", pd.Timestamp("2023-01-04 09:31:00", tz="Asia/Shanghai"), "ask")
    assert fill is not None
    assert fill["price"] == 10.6


def test_completed_net_formula_is_ask_minus_bid_times_100_minus_28():
    assert completed_net_cny(10.0, 13.0, 14.0, 14.0, 100.0) == 272.0


def test_adjudicate_2022_does_not_vote_and_requires_two_of_three_gate_years():
    ledger = pd.DataFrame(
        [
            {"status": "completed_two_leg", "entry_day": "2022-08-01", "net_cny": 100.0, "exit_class": "temporal_completion"},
            {"status": "completed_two_leg", "entry_day": "2023-03-01", "net_cny": 10.0, "exit_class": "temporal_completion"},
            {"status": "completed_two_leg", "entry_day": "2024-03-01", "net_cny": 8.0, "exit_class": "parent_failure"},
            {"status": "completed_two_leg", "entry_day": "2025-03-01", "net_cny": -5.0, "exit_class": "censored"},
            {"status": "option_entry_unavailable", "entry_day": "2024-06-01", "net_cny": None, "exit_class": None},
        ]
    )
    verdict = adjudicate(ledger)
    assert verdict["annual"]["2022"]["votes"] is False
    assert verdict["positive_gate_years"] == 2
    assert verdict["gates"]["annual_mean_net_positive_min_2_of_3"] is True
    assert verdict["n_completed_two_leg"] == 4
    assert verdict["missingness_counts"]["option_entry_unavailable"] == 1


def test_research_csv_pack_is_under_github_file_limit():
    repo = Path(__file__).resolve().parents[1]
    pack = repo / "data/r1b_research"
    assert (pack / "manifest.json").is_file()
    assert (pack / "contract_master.csv").is_file()
    years = {path.name[len("000852.SH_1m_") : -4] for path in (pack / "underlying_1m").glob("000852.SH_1m_*.csv")}
    assert years == {str(year) for year in range(2015, 2026)}
    oversize = [path for path in pack.rglob("*") if path.is_file() and path.stat().st_size > 90 * 1024 * 1024]
    assert oversize == []
    store = MonthlyQuoteStore(pack / "mo_quotes")
    assert store.available_months[0] == "2022-07"
    assert store.available_months[-1] == "2025-12"
    assert "2026-01" not in store.available_months


def test_frozen_ledger_reproduces_fail_identity_closed():
    repo = Path(__file__).resolve().parents[1]
    ledger = pd.read_csv(repo / "docs/ops/evidence/r1b_mo_outcome_20260911/event_ledger.csv")
    receipt = json.loads((repo / "docs/ops/evidence/r1b_mo_outcome_20260911/outcome_receipt.json").read_text(encoding="utf-8"))
    verdict = adjudicate(ledger)
    assert verdict["decision"] == "FAIL_IDENTITY_CLOSED"
    assert verdict["n_completed_two_leg"] == 366
    assert verdict["gates"] == receipt["adjudication"]["gates"]
    assert (ledger.entry_day.str[:4] == "2026").sum() == 0


def test_join_event_marks_entry_after_exit(tmp_path: Path):
    month = tmp_path / "mo_2023-01.csv"
    month.write_text(
        "contract_code,option_type,strike,expiry,timestamp,bid1,bid1_size,ask1,ask1_size,trading_status\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 10:00:00.000000,10.0,1,10.4,2,TRADING\n"
        "MO2302-C-6500,C,6500.0,2023-02-17,2023-01-04 10:01:00.000000,10.2,1,10.5,2,TRADING\n",
        encoding="utf-8",
    )
    event = UnderlyingEvent(
        confirm_idx=0,
        entry_idx=1,
        exit_idx=2,
        horizon_end_idx=1201,
        parent_sign=1,
        recovery=6600.0,
        failure=6400.0,
        entry_price=6500.0,
        exit_price=6510.0,
        confirm_day="2023-01-04",
        entry_day="2023-01-04",
        exit_day="2023-01-04",
        horizon_day="2023-01-11",
        confirm_ts=pd.Timestamp("2023-01-04 09:30:00", tz="Asia/Shanghai"),
        entry_ts=pd.Timestamp("2023-01-04 09:31:00", tz="Asia/Shanghai"),
        exit_ts=pd.Timestamp("2023-01-04 09:32:00", tz="Asia/Shanghai"),
        horizon_ts=pd.Timestamp("2023-01-11 14:00:00", tz="Asia/Shanghai"),
        structural_outcome="recovery",
        exit_class="temporal_completion",
        missingness=None,
        holding_bars=1,
    )
    freeze = {
        "primary_payoff": {
            "open_fee_cny": 14,
            "close_fee_cny": 14,
            "multiplier_cny_per_index_point": 100,
        }
    }
    row = join_event(event, MonthlyQuoteStore(tmp_path), freeze)
    assert row["status"] == "option_entry_after_exit"
    assert row["contract_code"] == "MO2302-C-6500"
