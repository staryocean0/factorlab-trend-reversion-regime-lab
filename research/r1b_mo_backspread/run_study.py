#!/usr/bin/env python3
"""Run the frozen R1B MO 1x2 adjacent-OTM ratio-backspread study exactly once.

No strike-width, ratio, DTE, event, horizon, exit, fee, year, regime or side search
is implemented here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from research.r1b_mo_backspread.selection import (
    completed_backspread_net_cny,
    entry_net_debit_cny,
    select_backspread_pair,
)
from research.r1b_mo_outcome.events import UnderlyingEvent, build_underlying_events
from research.r1b_mo_outcome.quotes import MonthlyQuoteStore, month_key, next_month

DEFAULT_FREEZE = Path("docs/governance/R1B_MO_BACKSPREAD_PRE_EXECUTION_FREEZE@1.0.json")
DEFAULT_QUOTES = Path("data/r1b_research/mo_quotes")
DEFAULT_UNDERLYING = Path("data/r1b_research/underlying_1m")
DEFAULT_RECEIPT = Path("docs/ops/evidence/r1b_mo_backspread_20260911/outcome_receipt.json")
DEFAULT_LEDGER = Path("docs/ops/evidence/r1b_mo_backspread_20260911/event_ledger.csv")
DEFAULT_REPORT = Path("docs/research/R1B_MO_RATIO_BACKSPREAD_OUTCOME_STUDY_20260911.md")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head(repo: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    except Exception:
        return None


def load_underlying(repo: Path) -> pd.DataFrame:
    root = repo / DEFAULT_UNDERLYING
    files = sorted(root.glob("000852.SH_1m_*.csv"))
    if not files:
        raise FileNotFoundError(f"no cloud underlying CSVs under {root}")
    frame = pd.concat((pd.read_csv(path) for path in files), ignore_index=True)
    frame["trading_day"] = frame["trading_day"].astype(str)
    frame["market_time_shanghai"] = pd.to_datetime(frame["timestamp"].astype(str).str[:19]).dt.tz_localize("Asia/Shanghai")
    if (pd.to_datetime(frame["trading_day"]).dt.date > date(2025, 12, 31)).any():
        raise RuntimeError("underlying CSV read past frozen admitted end 2025-12-31")
    return frame.sort_values("market_time_shanghai", kind="mergesort").reset_index(drop=True)


def _horizon_date(event: UnderlyingEvent) -> date | None:
    return date.fromisoformat(event.horizon_day) if event.horizon_day else None


def _joint_frame(store: MonthlyQuoteStore, key: str, short_code: str, long_code: str) -> pd.DataFrame:
    month = store.load_month(key)
    if month.empty:
        return pd.DataFrame()
    short = month.loc[month["contract_code"].astype(str) == short_code].copy()
    long = month.loc[month["contract_code"].astype(str) == long_code].copy()
    if short.empty or long.empty:
        return pd.DataFrame()
    short = short.drop_duplicates("timestamp", keep="last").set_index("timestamp")
    long = long.drop_duplicates("timestamp", keep="last").set_index("timestamp")
    joined = short.add_prefix("short_").join(long.add_prefix("long_"), how="inner")
    return joined.sort_index(kind="mergesort")


def first_joint_valid(
    store: MonthlyQuoteStore,
    *,
    short_code: str,
    long_code: str,
    start_ts: pd.Timestamp,
    phase: str,
) -> dict[str, Any] | None:
    if phase not in {"entry", "exit"}:
        raise ValueError("phase must be entry or exit")
    start = pd.Timestamp(start_ts)
    if start.tzinfo is None:
        start = start.tz_localize("Asia/Shanghai")
    else:
        start = start.tz_convert("Asia/Shanghai")
    if not store.available_months:
        return None
    key = month_key(start)
    last = store.available_months[-1]
    while key <= last:
        joined = _joint_frame(store, key, short_code, long_code)
        if not joined.empty:
            base = (
                (joined.index >= start)
                & (joined["short_trading_status"].astype(str) == "TRADING")
                & (joined["long_trading_status"].astype(str) == "TRADING")
            )
            if phase == "entry":
                valid = joined.loc[
                    base
                    & (joined["short_bid1"] > 0)
                    & (joined["short_bid1_size"] >= 1)
                    & (joined["long_ask1"] > 0)
                    & (joined["long_ask1_size"] >= 2)
                ]
                if not valid.empty:
                    ts = valid.index[0]
                    row = valid.iloc[0]
                    return {
                        "timestamp": ts,
                        "short_price": float(row["short_bid1"]),
                        "short_size": float(row["short_bid1_size"]),
                        "long_price": float(row["long_ask1"]),
                        "long_size": float(row["long_ask1_size"]),
                    }
            else:
                valid = joined.loc[
                    base
                    & (joined["short_ask1"] > 0)
                    & (joined["short_ask1_size"] >= 1)
                    & (joined["long_bid1"] > 0)
                    & (joined["long_bid1_size"] >= 2)
                ]
                if not valid.empty:
                    ts = valid.index[0]
                    row = valid.iloc[0]
                    return {
                        "timestamp": ts,
                        "short_price": float(row["short_ask1"]),
                        "short_size": float(row["short_ask1_size"]),
                        "long_price": float(row["long_bid1"]),
                        "long_size": float(row["long_bid1_size"]),
                    }
        key = next_month(key)
    return None


def join_event(event: UnderlyingEvent, store: MonthlyQuoteStore, freeze: dict[str, Any]) -> dict[str, Any]:
    option_type = "C" if event.parent_sign > 0 else "P"
    base: dict[str, Any] = {
        "confirm_idx": event.confirm_idx,
        "entry_idx": event.entry_idx,
        "exit_idx": event.exit_idx,
        "parent_sign": event.parent_sign,
        "option_type": option_type,
        "entry_day": event.entry_day,
        "exit_day": event.exit_day,
        "entry_ts": str(event.entry_ts),
        "exit_ts": None if event.exit_ts is None else str(event.exit_ts),
        "entry_spot": event.entry_price,
        "exit_spot": event.exit_price,
        "exit_class": event.exit_class,
        "holding_bars": event.holding_bars,
        "short_contract": None,
        "long_contract": None,
        "expiry": None,
        "short_atm_strike": None,
        "long_otm_strike": None,
        "spread_width_points": None,
        "joint_entry_ts": None,
        "joint_exit_ts": None,
        "short_entry_bid": None,
        "short_exit_ask": None,
        "long_entry_ask": None,
        "long_exit_bid": None,
        "entry_net_debit_cny_before_fees": None,
        "exit_value_cny_before_fees": None,
        "spot_move": None,
        "net_cny": None,
    }
    if event.missingness:
        return {**base, "status": event.missingness}
    horizon = _horizon_date(event)
    if horizon is None:
        return {**base, "status": "underlying_horizon_truncated"}
    pair = select_backspread_pair(store.contract_master(), float(event.entry_price), option_type, horizon)
    if pair is None:
        return {**base, "status": "pair_unavailable"}
    base.update(
        {
            "short_contract": pair.short_atm.contract_code,
            "long_contract": pair.long_otm.contract_code,
            "expiry": pair.short_atm.expiry.isoformat(),
            "short_atm_strike": pair.short_atm.strike,
            "long_otm_strike": pair.long_otm.strike,
            "spread_width_points": abs(pair.long_otm.strike - pair.short_atm.strike),
        }
    )
    entry = first_joint_valid(
        store,
        short_code=pair.short_atm.contract_code,
        long_code=pair.long_otm.contract_code,
        start_ts=event.entry_ts,
        phase="entry",
    )
    if entry is None:
        return {**base, "status": "joint_entry_unavailable"}
    if event.exit_ts is None or entry["timestamp"] >= event.exit_ts:
        return {**base, "joint_entry_ts": str(entry["timestamp"]), "status": "joint_entry_after_exit"}
    exit_fill = first_joint_valid(
        store,
        short_code=pair.short_atm.contract_code,
        long_code=pair.long_otm.contract_code,
        start_ts=event.exit_ts,
        phase="exit",
    )
    if exit_fill is None:
        return {**base, "joint_entry_ts": str(entry["timestamp"]), "status": "joint_exit_unavailable"}
    fee = float(freeze["fee_contract"]["fee_cny_per_contract_per_leg"])
    mult = float(freeze["instrument_mapping"]["multiplier_cny_per_index_point"])
    net = completed_backspread_net_cny(
        short_entry_bid=entry["short_price"],
        short_exit_ask=exit_fill["short_price"],
        long_entry_ask=entry["long_price"],
        long_exit_bid=exit_fill["long_price"],
        multiplier=mult,
        fee_per_contract_per_leg=fee,
    )
    entry_debit = entry_net_debit_cny(entry["short_price"], entry["long_price"], mult)
    exit_value = (2.0 * exit_fill["long_price"] - exit_fill["short_price"]) * mult
    return {
        **base,
        "joint_entry_ts": str(entry["timestamp"]),
        "joint_exit_ts": str(exit_fill["timestamp"]),
        "short_entry_bid": entry["short_price"],
        "short_exit_ask": exit_fill["short_price"],
        "long_entry_ask": entry["long_price"],
        "long_exit_bid": exit_fill["long_price"],
        "entry_net_debit_cny_before_fees": entry_debit,
        "exit_value_cny_before_fees": exit_value,
        "spot_move": None if event.exit_price is None else event.exit_price / event.entry_price - 1.0,
        "net_cny": net,
        "status": "completed_backspread",
    }


def adjudicate(ledger: pd.DataFrame, freeze: dict[str, Any]) -> dict[str, Any]:
    completed = ledger.loc[ledger["status"] == "completed_backspread"].copy()
    n_joinable = int(len(ledger))
    n_completed = int(len(completed))
    coverage = n_completed / n_joinable if n_joinable else 0.0
    pooled_mean = float(completed["net_cny"].mean()) if n_completed else None
    pooled_median = float(completed["net_cny"].median()) if n_completed else None
    win_rate = float((completed["net_cny"] > 0).mean()) if n_completed else None

    completed["year"] = pd.to_datetime(completed["entry_day"]).dt.year if n_completed else pd.Series(dtype=int)
    completed["quarter"] = pd.to_datetime(completed["entry_day"]).dt.to_period("Q").astype(str) if n_completed else pd.Series(dtype=str)
    gate_years = [int(x) for x in freeze["viability_gates"]["annual_mean_net_year_set"]]
    annual_means = {
        str(year): (float(completed.loc[completed["year"] == year, "net_cny"].mean()) if (completed["year"] == year).any() else None)
        for year in gate_years
    }
    annual_positive = sum(value is not None and value > 0 for value in annual_means.values())

    quarter_names = [f"{y}Q{q}" for y in range(2023, 2026) for q in range(1, 5)]
    quarterly_means = {
        q: (float(completed.loc[completed["quarter"] == q, "net_cny"].mean()) if (completed["quarter"] == q).any() else None)
        for q in quarter_names
    }
    quarterly_positive = sum(value is not None and value > 0 for value in quarterly_means.values())

    gates = freeze["viability_gates"]
    gate_results = {
        "joint_fill_coverage": coverage >= float(gates["joint_fill_coverage_min_fraction"]),
        "pooled_mean_net_positive": pooled_mean is not None and pooled_mean > 0,
        "annual_mean_positive_min_years": annual_positive >= int(gates["annual_mean_net_positive_min_years"]),
        "quarterly_mean_positive_min_quarters": quarterly_positive >= int(gates["quarterly_mean_net_positive_min_quarters"]),
    }
    passed = all(gate_results.values())
    return {
        "decision": "PASS_RESEARCH_CANDIDATE_ACCOUNT_AUDIT_REQUIRED" if passed else "FAIL_IDENTITY_CLOSED",
        "passed": passed,
        "n_joinable_underlying_events": n_joinable,
        "n_completed_backspread": n_completed,
        "joint_fill_coverage": coverage,
        "pooled_mean_net_cny": pooled_mean,
        "pooled_median_net_cny_descriptive": pooled_median,
        "win_rate_descriptive": win_rate,
        "annual_mean_net_cny": annual_means,
        "annual_positive_years": annual_positive,
        "quarterly_mean_net_cny": quarterly_means,
        "quarterly_positive_quarters": quarterly_positive,
        "gate_results": gate_results,
    }


def render_report(receipt: dict[str, Any]) -> str:
    a = receipt["adjudication"]
    status_counts = receipt["status_counts"]
    annual = "\n".join(f"| {y} | {v if v is not None else 'NA'} |" for y, v in a["annual_mean_net_cny"].items())
    quarterly = "\n".join(f"| {q} | {v if v is not None else 'NA'} |" for q, v in a["quarterly_mean_net_cny"].items())
    gates = "\n".join(f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in a["gate_results"].items())
    statuses = "\n".join(f"- `{k}`: {v}" for k, v in status_counts.items())
    return f"""# R1_B MO 1x2 adjacent-OTM ratio-backspread outcome study — 2026-09-11

Research identity: `rmr_R1B_MO_ratio_backspread_v1`

Candidate: `R1B_MO_1x2_ADJACENT_OTM_RATIO_BACKSPREAD_SAME_CAUSAL_EXIT`

Decision: **{a['decision']}**

`fresh_oos=false`  
`BLACKBOX_query_count=3`  
`production_authority=false`

Freeze: `docs/governance/R1B_MO_BACKSPREAD_PRE_EXECUTION_FREEZE@1.0.json`

## Frozen mapping

The R1_B event engine, S2/S3 thresholds, parent direction, next-1m-close entry, causal success/failure exit, 1200-bar safety horizon, expiry rule and 14 CNY/contract/leg fee are inherited unchanged. The new payoff object sells one deterministic ATM directional option and buys two immediately adjacent OTM options of the same type and expiry. Both legs execute only at a common valid quote timestamp.

No spread-width, ratio, DTE, horizon, exit, filter, side, year or fee search was performed.

## Inventory

- joinable underlying events: **{a['n_joinable_underlying_events']}**
- completed joint-fill backspreads: **{a['n_completed_backspread']}**
- joint-fill coverage: **{a['joint_fill_coverage']:.4%}**
- descriptive pooled mean net CNY: **{a['pooled_mean_net_cny']}**
- descriptive pooled median net CNY: **{a['pooled_median_net_cny_descriptive']}**
- descriptive win rate: **{a['win_rate_descriptive']}**

Status counts:

{statuses}

## Sealed gates

| Gate | Result |
|---|---|
{gates}

Annual positive years: **{a['annual_positive_years']}/3**.
Quarterly positive quarters: **{a['quarterly_positive_quarters']}/12**.

### Annual mean net CNY

| Year | Mean |
|---|---:|
{annual}

### Quarterly mean net CNY

| Quarter | Mean |
|---|---:|
{quarterly}

## Adjudication

This result is mechanically adjudicated from the precommitted gates. A failure closes this identity with no retune. A pass would create only a research candidate and would still require a separate short-option spread-margin/account-capital audit; it would not authorize BLACKBOX #4 or production.
"""


def run_study(repo: Path, freeze_path: Path, receipt_path: Path, ledger_path: Path, report_path: Path) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze["research_identity"] != "rmr_R1B_MO_ratio_backspread_v1":
        raise RuntimeError("unexpected research identity")
    if freeze.get("blackbox_query_4_authorized") is True or freeze.get("production_authority") is True:
        raise RuntimeError("forbidden authority in freeze")
    underlying = load_underlying(repo)
    events = build_underlying_events(underlying)
    store = MonthlyQuoteStore(repo / DEFAULT_QUOTES)
    _ = store.contract_master()
    rows: list[dict[str, Any]] = []
    for i, event in enumerate(events, start=1):
        rows.append(join_event(event, store, freeze))
        if i == 1 or i % 25 == 0 or i == len(events):
            print(f"joined {i}/{len(events)} status={rows[-1]['status']}", flush=True)
    ledger = pd.DataFrame(rows)
    verdict = adjudicate(ledger, freeze)
    receipt = {
        "schema_id": "rmr_R1B_MO_ratio_backspread_outcome_receipt@1.0",
        "research_identity": freeze["research_identity"],
        "candidate_id": freeze["candidate_id"],
        "freeze_path": str(freeze_path.relative_to(repo)),
        "freeze_sha256": sha256_file(freeze_path),
        "code_commit": git_head(repo),
        "fresh_oos": False,
        "blackbox_query_count": 3,
        "blackbox_query_4_authorized": False,
        "production_authority": False,
        "threshold_retune_after_results": False,
        "status_counts": {str(k): int(v) for k, v in ledger["status"].value_counts().to_dict().items()},
        "adjudication": verdict,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(ledger_path, index=False)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render_report(receipt), encoding="utf-8")
    return receipt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path("."))
    p.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    p.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    p.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    p.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = p.parse_args()
    repo = args.repo_root.resolve()
    receipt = run_study(
        repo,
        repo / args.freeze,
        repo / args.receipt,
        repo / args.ledger,
        repo / args.report,
    )
    print(json.dumps(receipt["adjudication"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
