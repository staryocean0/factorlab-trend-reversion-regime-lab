"""Monthly MO L1 lookup for the frozen ATM ask-in / bid-out clocks."""
from __future__ import annotations

from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from research.r1b_mo_pre_execution.selection import CandidateContract, select_contract

QUOTE_COLUMNS = [
    "contract_code",
    "option_type",
    "strike",
    "expiry",
    "timestamp",
    "bid1",
    "bid1_size",
    "ask1",
    "ask1_size",
    "trading_status",
]


def _to_shanghai(value) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        return ts.tz_localize("Asia/Shanghai")
    return ts.tz_convert("Asia/Shanghai")


def month_key(ts: pd.Timestamp | datetime | date) -> str:
    if isinstance(ts, date) and not isinstance(ts, datetime):
        return f"{ts.year:04d}-{ts.month:02d}"
    stamp = _to_shanghai(ts)
    return f"{stamp.year:04d}-{stamp.month:02d}"


def next_month(key: str) -> str:
    year, month = int(key[:4]), int(key[5:7])
    if month == 12:
        return f"{year + 1:04d}-01"
    return f"{year:04d}-{month + 1:02d}"


def month_from_quote_name(name: str) -> str | None:
    stem = name[:-4] if name.endswith(".csv") else name
    if not stem.startswith("mo_"):
        return None
    rest = stem[3:]
    if len(rest) >= 7 and rest[4] == "-":
        return rest[:7]
    return None


class MonthlyQuoteStore:
    def __init__(self, quotes_dir: Path, cache_months: int = 4, master_path: Path | None = None) -> None:
        self.quotes_dir = Path(quotes_dir)
        self.cache_months = cache_months
        self._month_cache: OrderedDict[str, pd.DataFrame] = OrderedDict()
        self._master: list[CandidateContract] | None = None
        default_master = self.quotes_dir.parent / "contract_master.csv"
        self.master_path = Path(master_path) if master_path else default_master
        months = {month_from_quote_name(path.name) for path in self.quotes_dir.glob("mo_*.csv")}
        self.available_months = sorted(month for month in months if month)

    def _month_paths(self, key: str) -> list[Path]:
        paths: list[Path] = []
        exact = self.quotes_dir / f"mo_{key}.csv"
        if exact.is_file():
            paths.append(exact)
        paths.extend(sorted(self.quotes_dir.glob(f"mo_{key}-??.csv")))
        paths.extend(sorted(self.quotes_dir.glob(f"mo_{key}_p*.csv")))
        return paths

    def load_month(self, key: str) -> pd.DataFrame:
        if key in self._month_cache:
            self._month_cache.move_to_end(key)
            return self._month_cache[key]
        paths = self._month_paths(key)
        if not paths:
            frame = pd.DataFrame(columns=QUOTE_COLUMNS)
        else:
            parts = [pd.read_csv(path, usecols=QUOTE_COLUMNS) for path in paths]
            frame = pd.concat(parts, ignore_index=True)
            frame["timestamp"] = pd.to_datetime(frame["timestamp"]).dt.tz_localize("Asia/Shanghai")
            frame["expiry"] = pd.to_datetime(frame["expiry"]).dt.date
            frame["option_type"] = frame["option_type"].astype(str).str.upper()
            frame = frame.sort_values(["contract_code", "timestamp"], kind="mergesort").reset_index(drop=True)
        self._month_cache[key] = frame
        while len(self._month_cache) > self.cache_months:
            self._month_cache.popitem(last=False)
        return frame

    def contract_master(self) -> list[CandidateContract]:
        if self._master is not None:
            return self._master
        if self.master_path.is_file():
            frame = pd.read_csv(
                self.master_path,
                usecols=["contract_code", "option_type", "strike", "expiry"],
                dtype={"contract_code": "string", "option_type": "string", "expiry": "string"},
            )
            self._master = [
                CandidateContract(
                    contract_code=str(rec.contract_code),
                    option_type=str(rec.option_type).upper(),
                    strike=float(rec.strike),
                    expiry=date.fromisoformat(str(rec.expiry)[:10]),
                )
                for rec in frame.itertuples(index=False)
            ]
            return self._master
        seen: dict[str, CandidateContract] = {}
        for key in self.available_months:
            for path in self._month_paths(key):
                frame = pd.read_csv(
                    path,
                    usecols=["contract_code", "option_type", "strike", "expiry"],
                    dtype={"contract_code": "string", "option_type": "string", "expiry": "string"},
                )
                frame = frame.drop_duplicates("contract_code", keep="first")
                for rec in frame.itertuples(index=False):
                    code = str(rec.contract_code)
                    if code in seen:
                        continue
                    seen[code] = CandidateContract(
                        contract_code=code,
                        option_type=str(rec.option_type).upper(),
                        strike=float(rec.strike),
                        expiry=date.fromisoformat(str(rec.expiry)[:10]),
                    )
        self._master = list(seen.values())
        return self._master

    def select(self, spot: float, option_type: str, horizon_date: date) -> CandidateContract | None:
        return select_contract(self.contract_master(), spot, option_type, horizon_date)

    def first_valid(
        self,
        contract_code: str,
        start_ts: pd.Timestamp,
        side: str,
    ) -> dict | None:
        if side not in {"ask", "bid"}:
            raise ValueError("side must be ask or bid")
        start = _to_shanghai(start_ts)
        key = month_key(start)
        price_col = "ask1" if side == "ask" else "bid1"
        size_col = "ask1_size" if side == "ask" else "bid1_size"
        while key <= (self.available_months[-1] if self.available_months else ""):
            month = self.load_month(key)
            if month.empty:
                if key not in self.available_months:
                    return None
                key = next_month(key)
                continue
            block = month.loc[month["contract_code"].astype(str) == contract_code]
            if not block.empty:
                valid = block.loc[
                    (block["timestamp"] >= start)
                    & (block["trading_status"].astype(str) == "TRADING")
                    & (block[price_col] > 0)
                    & (block[size_col] > 0)
                ]
                if not valid.empty:
                    row = valid.iloc[0]
                    return {
                        "contract_code": str(row["contract_code"]),
                        "timestamp": row["timestamp"],
                        "price": float(row[price_col]),
                        "size": float(row[size_col]),
                    }
            if key not in self.available_months and not self._month_paths(key):
                return None
            key = next_month(key)
        return None
