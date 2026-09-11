"""Deterministic contract-selection primitives for the frozen R1B MO mapping.

These functions do not read market tapes or event outcomes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class CandidateContract:
    contract_code: str
    option_type: str
    strike: float
    expiry: date


def horizon_end_idx(entry_idx: int, horizon_bars: int) -> int:
    if entry_idx < 0:
        raise ValueError("entry_idx must be >= 0")
    if horizon_bars <= 0:
        raise ValueError("horizon_bars must be > 0")
    return entry_idx + horizon_bars


def select_expiry(candidates: list[CandidateContract], horizon_date: date) -> date | None:
    eligible = [item for item in candidates if item.expiry > horizon_date]
    if not eligible:
        return None
    return min(item.expiry for item in eligible)


def select_strike(
    candidates: list[CandidateContract],
    spot: float,
    option_type: str,
) -> CandidateContract:
    if option_type not in {"C", "P"}:
        raise ValueError("option_type must be C or P")
    pool = [item for item in candidates if item.option_type == option_type]
    if not pool:
        raise ValueError("no candidates of the required option type")
    best_distance = min(abs(item.strike - spot) for item in pool)
    tied = [item for item in pool if abs(item.strike - spot) == best_distance]
    if option_type == "C":
        otm_strike = max(item.strike for item in tied)
    else:
        otm_strike = min(item.strike for item in tied)
    finalists = [item for item in tied if item.strike == otm_strike]
    return min(finalists, key=lambda item: item.contract_code)


def select_contract(
    candidates: list[CandidateContract],
    spot: float,
    option_type: str,
    horizon_date: date,
) -> CandidateContract | None:
    expiry = select_expiry(candidates, horizon_date)
    if expiry is None:
        return None
    same_expiry = [item for item in candidates if item.expiry == expiry and item.option_type == option_type]
    if not same_expiry:
        return None
    return select_strike(same_expiry, spot, option_type)


def completed_net_cny(entry_ask: float, exit_bid: float, open_fee: float, close_fee: float, multiplier: float) -> float:
    return (exit_bid - entry_ask) * multiplier - open_fee - close_fee
