#!/usr/bin/env python3
"""Execute the frozen R1B MO ATM directional-long outcome study.

This runner may only consume the pre-execution freeze. It does not search
strikes, DTE, horizons, thresholds, or costs.
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

from regime_lab.market_data import load_market_data
from research.r1b_mo_outcome.adjudicate import adjudicate
from research.r1b_mo_outcome.events import UnderlyingEvent, build_underlying_events
from research.r1b_mo_outcome.quotes import MonthlyQuoteStore
from research.r1b_mo_pre_execution.selection import completed_net_cny

DEFAULT_FREEZE = Path("docs/governance/R1B_MO_PRE_EXECUTION_FREEZE@1.0.json")
DEFAULT_QUOTES = Path("data/r1b_research/mo_quotes")
FALLBACK_QUOTES = Path("data/r1b_mo_admission/datahub/quotes")
RESEARCH_1M = Path("data/r1b_research/underlying_1m")
DEFAULT_RECEIPT = Path("docs/ops/evidence/r1b_mo_outcome_20260911/outcome_receipt.json")
DEFAULT_LEDGER = Path("docs/ops/evidence/r1b_mo_outcome_20260911/event_ledger.csv")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_digest(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    return hashlib.sha256(raw).hexdigest()


def git_head(repo: Path) -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
    except Exception:
        return None


def mapping_digest(freeze: dict[str, Any]) -> str:
    return json_digest(
        {
            "inherited_r1b_clock": freeze["inherited_r1b_clock"],
            "option_mapping": freeze["option_mapping"],
            "primary_payoff": freeze["primary_payoff"],
            "viability_gates": freeze["viability_gates"],
            "joinable_evaluation_window": freeze["joinable_evaluation_window"],
        }
    )


def _horizon_date(event: UnderlyingEvent) -> date | None:
    if event.horizon_day:
        return date.fromisoformat(event.horizon_day)
    return None


def _intrinsic(spot: float, strike: float, option_type: str) -> float:
    if option_type == "C":
        return max(spot - strike, 0.0)
    return max(strike - spot, 0.0)


def _multiplier(freeze: dict[str, Any]) -> float:
    mapping = freeze.get("option_mapping", {})
    payoff = freeze.get("primary_payoff", {})
    if "multiplier_cny_per_index_point" in mapping:
        return float(mapping["multiplier_cny_per_index_point"])
    return float(payoff["multiplier_cny_per_index_point"])


def resolve_quotes_dir(repo: Path, quotes_dir: Path) -> Path:
    if quotes_dir.is_dir() and any(quotes_dir.glob("mo_*.csv")):
        return quotes_dir
    fallback = repo / FALLBACK_QUOTES
    if fallback.is_dir() and any(fallback.glob("mo_*.csv")):
        return fallback
    return quotes_dir


def load_underlying(repo: Path, freeze: dict[str, Any]) -> pd.DataFrame:
    csv_dir = repo / RESEARCH_1M
    files = sorted(csv_dir.glob("000852.SH_1m_*.csv")) if csv_dir.is_dir() else []
    if files:
        frame = pd.concat((pd.read_csv(path) for path in files), ignore_index=True)
        frame["trading_day"] = frame["trading_day"].astype(str)
        frame["market_time_shanghai"] = pd.to_datetime(frame["timestamp"].astype(str).str[:19]).dt.tz_localize("Asia/Shanghai")
        if (pd.to_datetime(frame["trading_day"]).dt.date > date.fromisoformat("2025-12-31")).any():
            raise RuntimeError("underlying CSV read past admitted end")
        return frame.sort_values("market_time_shanghai", kind="mergesort").reset_index(drop=True)
    binding = freeze["underlying_binding"]
    return load_market_data(
        binding["symbol"],
        binding["frequency"],
        "2015-01-05",
        binding["admitted_end"],
        root=repo,
    )


def join_event(event: UnderlyingEvent, store: MonthlyQuoteStore, freeze: dict[str, Any]) -> dict[str, Any]:
    payoff = freeze["primary_payoff"]
    multiplier = _multiplier(freeze)
    option_type = "C" if event.parent_sign > 0 else "P"
    base = {
        "confirm_idx": event.confirm_idx,
        "entry_idx": event.entry_idx,
        "exit_idx": event.exit_idx,
        "horizon_end_idx": event.horizon_end_idx,
        "parent_sign": event.parent_sign,
        "option_type": option_type,
        "confirm_day": event.confirm_day,
        "entry_day": event.entry_day,
        "exit_day": event.exit_day,
        "horizon_day": event.horizon_day,
        "entry_ts": str(event.entry_ts),
        "exit_ts": None if event.exit_ts is None else str(event.exit_ts),
        "entry_spot": event.entry_price,
        "exit_spot": event.exit_price,
        "exit_class": event.exit_class,
        "holding_bars": event.holding_bars,
        "structural_outcome": event.structural_outcome,
        "contract_code": None,
        "expiry": None,
        "strike": None,
        "entry_ask": None,
        "exit_bid": None,
        "option_entry_ts": None,
        "option_exit_ts": None,
        "net_cny": None,
        "premium_return": None,
        "entry_premium_cny": None,
        "exit_premium_cny": None,
        "intrinsic_at_entry": None,
        "time_to_expiry_days": None,
        "spot_move": None,
    }
    if event.missingness:
        return {**base, "status": event.missingness}
    horizon = _horizon_date(event)
    if horizon is None:
        return {**base, "status": "underlying_horizon_truncated"}
    if not store.available_months:
        return {**base, "status": "window_unjoinable"}
    chosen = store.select(float(event.entry_price), option_type, horizon)
    if chosen is None:
        return {**base, "status": "option_entry_unavailable"}
    base.update(
        {
            "contract_code": chosen.contract_code,
            "expiry": chosen.expiry.isoformat(),
            "strike": chosen.strike,
            "intrinsic_at_entry": _intrinsic(float(event.entry_price), chosen.strike, option_type),
            "time_to_expiry_days": (chosen.expiry - date.fromisoformat(event.entry_day)).days,
        }
    )
    ask = store.first_valid(chosen.contract_code, event.entry_ts, "ask")
    if ask is None:
        return {**base, "status": "option_entry_unavailable"}
    if event.exit_ts is None or ask["timestamp"] >= event.exit_ts:
        return {
            **base,
            "entry_ask": ask["price"],
            "option_entry_ts": str(ask["timestamp"]),
            "entry_premium_cny": ask["price"] * multiplier,
            "status": "option_entry_after_exit",
        }
    bid = store.first_valid(chosen.contract_code, event.exit_ts, "bid")
    if bid is None:
        return {
            **base,
            "entry_ask": ask["price"],
            "option_entry_ts": str(ask["timestamp"]),
            "entry_premium_cny": ask["price"] * multiplier,
            "status": "option_exit_unavailable",
        }
    net = completed_net_cny(
        ask["price"],
        bid["price"],
        float(payoff["open_fee_cny"]),
        float(payoff["close_fee_cny"]),
        multiplier,
    )
    entry_premium = ask["price"] * multiplier
    exit_premium = bid["price"] * multiplier
    return {
        **base,
        "entry_ask": ask["price"],
        "exit_bid": bid["price"],
        "option_entry_ts": str(ask["timestamp"]),
        "option_exit_ts": str(bid["timestamp"]),
        "entry_premium_cny": entry_premium,
        "exit_premium_cny": exit_premium,
        "net_cny": net,
        "premium_return": (bid["price"] / ask["price"] - 1.0) if ask["price"] else None,
        "spot_move": None if event.exit_price is None else event.exit_price / event.entry_price - 1.0,
        "status": "completed_two_leg",
    }


def run_study(
    *,
    repo: Path,
    freeze_path: Path,
    quotes_dir: Path,
    receipt_path: Path,
    ledger_path: Path,
    underlying: pd.DataFrame | None = None,
) -> dict[str, Any]:
    freeze = json.loads(freeze_path.read_text(encoding="utf-8"))
    if freeze.get("empirical_option_outcome_test_authorized") is not True:
        raise RuntimeError("outcome study is not authorized")
    if freeze.get("outcome_runner_authorized") is not True:
        raise RuntimeError("outcome runner is not authorized")
    if freeze.get("blackbox_query_4_authorized") is True:
        raise RuntimeError("query #4 must stay closed")
    if freeze.get("production_authority") is True:
        raise RuntimeError("production authority must stay false")
    if underlying is None:
        underlying = load_underlying(repo, freeze)
    if (pd.to_datetime(underlying["trading_day"]).dt.date > date.fromisoformat("2025-12-31")).any():
        raise RuntimeError("underlying frame read past admitted end")
    print(f"underlying_rows={len(underlying)}", flush=True)
    events = build_underlying_events(underlying)
    print(f"joinable_underlying_events={len(events)}", flush=True)
    store = MonthlyQuoteStore(quotes_dir)
    print(f"quote_months={len(store.available_months)} building_contract_master", flush=True)
    n_contracts = len(store.contract_master())
    print(f"contract_master={n_contracts}", flush=True)
    rows = []
    for i, event in enumerate(events, start=1):
        rows.append(join_event(event, store, freeze))
        if i == 1 or i == len(events) or i % 25 == 0:
            print(f"joined {i}/{len(events)} last_status={rows[-1]['status']}", flush=True)
    ledger = pd.DataFrame(rows)
    verdict = adjudicate(ledger)
    receipt = {
        "schema_id": "rmr_R1B_MO_outcome_study_receipt@1.0",
        "research_identity": freeze["research_identity"],
        "candidate_id": freeze["candidate_id"],
        "freeze_path": str(freeze_path),
        "freeze_sha256": sha256_file(freeze_path),
        "mapping_digest": mapping_digest(freeze),
        "code_commit": git_head(repo),
        "quotes_dir": str(quotes_dir),
        "joinable_window": freeze["joinable_evaluation_window"],
        "adjudication": verdict,
        "threshold_retune_after_results": False,
        "fresh_oos": False,
        "production_authority": False,
        "blackbox_query_count": 3,
        "blackbox_query_4_authorized": False,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(ledger_path, index=False)
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the frozen R1B MO outcome study.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--freeze", type=Path, default=DEFAULT_FREEZE)
    parser.add_argument("--quotes-dir", type=Path, default=DEFAULT_QUOTES)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    args = parser.parse_args()
    receipt = run_study(
        repo=args.repo_root.resolve(),
        freeze_path=args.freeze if args.freeze.is_absolute() else args.repo_root / args.freeze,
        quotes_dir=resolve_quotes_dir(
            args.repo_root.resolve(),
            args.quotes_dir if args.quotes_dir.is_absolute() else args.repo_root / args.quotes_dir,
        ),
        receipt_path=args.receipt if args.receipt.is_absolute() else args.repo_root / args.receipt,
        ledger_path=args.ledger if args.ledger.is_absolute() else args.repo_root / args.ledger,
    )
    print(json.dumps(receipt["adjudication"], ensure_ascii=False, indent=2))
    return 0 if receipt["adjudication"]["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
