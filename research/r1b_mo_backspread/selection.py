from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from research.r1b_mo_pre_execution.selection import CandidateContract, select_expiry, select_strike


@dataclass(frozen=True)
class BackspreadPair:
    short_atm: CandidateContract
    long_otm: CandidateContract


def select_backspread_pair(
    candidates: list[CandidateContract],
    spot: float,
    option_type: str,
    horizon_date: date,
) -> BackspreadPair | None:
    """Select the frozen 1x2 pair without searching spread width.

    Short leg is the exact deterministic ATM contract from the prior frozen mapping.
    Long leg is the immediately adjacent listed strike farther OTM in the same expiry.
    """
    if option_type not in {"C", "P"}:
        raise ValueError("option_type must be C or P")
    expiry = select_expiry(candidates, horizon_date)
    if expiry is None:
        return None
    same = [c for c in candidates if c.expiry == expiry and c.option_type == option_type]
    if not same:
        return None
    short = select_strike(same, spot, option_type)
    if option_type == "C":
        farther = [c for c in same if c.strike > short.strike]
        if not farther:
            return None
        next_strike = min(c.strike for c in farther)
    else:
        farther = [c for c in same if c.strike < short.strike]
        if not farther:
            return None
        next_strike = max(c.strike for c in farther)
    finalists = [c for c in farther if c.strike == next_strike]
    long = min(finalists, key=lambda c: c.contract_code)
    return BackspreadPair(short_atm=short, long_otm=long)


def completed_backspread_net_cny(
    *,
    short_entry_bid: float,
    short_exit_ask: float,
    long_entry_ask: float,
    long_exit_bid: float,
    multiplier: float = 100.0,
    fee_per_contract_per_leg: float = 14.0,
) -> float:
    gross = (
        short_entry_bid
        - short_exit_ask
        + 2.0 * (long_exit_bid - long_entry_ask)
    ) * multiplier
    total_fee = fee_per_contract_per_leg * 6.0
    return gross - total_fee


def entry_net_debit_cny(
    short_entry_bid: float,
    long_entry_ask: float,
    multiplier: float = 100.0,
) -> float:
    """Positive means cash paid before fees; negative means entry credit."""
    return (2.0 * long_entry_ask - short_entry_bid) * multiplier
