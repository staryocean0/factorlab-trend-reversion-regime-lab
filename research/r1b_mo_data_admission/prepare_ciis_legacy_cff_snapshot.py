#!/usr/bin/env python3
"""Prepare CIIS legacy CFFEX Snapshot XLSX (headerless) for the MO adapter.

The CIIS public sample workbook stores positional columns matching manual section
6.6.1 without a CSV header row. This helper assigns documented field names,
derives quote validity (the native CFF snapshot layout has no trading-status
column), and emits adapter-ready CSV plus an MO contract master.

Adapter success remains ADAPTED_NOT_ADMITTED; this tool does not create admission
authority or authorize option outcomes.
"""
from __future__ import annotations

import argparse
import calendar
import json
import re
from dataclasses import asdict, dataclass
from datetime import date, datetime
from pathlib import Path

import pandas as pd

LEGACY_COLUMN_ORDER: list[str] = [
    "SecurityID",
    "DateTime",
    "SettlementGroupID",
    "SettlementID",
    "LastPrice",
    "PreSettlementPrice",
    "PreClosePrice",
    "PreOpenInterest",
    "OpenPrice",
    "HighPrice",
    "LowPrice",
    "Volume",
    "Turnover",
    "AveragePrice",
    "OpenInterest",
    "ClosePrice",
    "SettlementPrice",
    "UpperLimitPrice",
    "LowerLimitPrice",
    "PreDelta",
    "CurrDelta",
    "BidPrice1",
    "BidPrice2",
    "BidPrice3",
    "BidPrice4",
    "BidPrice5",
    "BidVolume1",
    "BidVolume2",
    "BidVolume3",
    "BidVolume4",
    "BidVolume5",
    "AskPrice1",
    "AskPrice2",
    "AskPrice3",
    "AskPrice4",
    "AskPrice5",
    "AskVolume1",
    "AskVolume2",
    "AskVolume3",
    "AskVolume4",
    "AskVolume5",
]

MO_CODE_RE = re.compile(r"^MO(\d{4})-[CP]-(\d+(?:\.\d+)?)$")

CONTINUOUS_SESSIONS = (
    ((9, 30), (11, 30)),
    ((13, 0), (15, 0)),
)


@dataclass
class PrepareReceipt:
    prepare_id: str
    source_xlsx: str
    snapshot_csv: str
    contract_master_csv: str
    source_rows: int
    mo_rows: int
    contract_master_rows: int
    sample_date: str
    derived_quote_status_counts: dict[str, int]
    column_count: int
    empirical_option_outcome_test_authorized: bool = False
    blackbox_query_count: int = 3
    production_authority: bool = False


def _third_friday(year: int, month: int) -> date:
    cal = calendar.Calendar(firstweekday=calendar.MONDAY)
    fridays = [
        day
        for day in cal.itermonthdates(year, month)
        if day.month == month and day.weekday() == calendar.FRIDAY
    ]
    if len(fridays) < 3:
        raise ValueError(f"cannot resolve third Friday for {year}-{month:02d}")
    return fridays[2]


def mo_expiry_from_contract_code(contract_code: str) -> str:
    match = MO_CODE_RE.fullmatch(contract_code)
    if not match:
        raise ValueError(f"not an MO contract code: {contract_code}")
    yymm = match.group(1)
    year = 2000 + int(yymm[:2])
    month = int(yymm[2:])
    return _third_friday(year, month).isoformat()


def _in_continuous_session(ts: datetime) -> bool:
    minutes = ts.hour * 60 + ts.minute
    for (sh, sm), (eh, em) in CONTINUOUS_SESSIONS:
        start = sh * 60 + sm
        end = eh * 60 + em
        if start <= minutes <= end:
            return True
    return False


def derive_quote_status(row: pd.Series) -> str:
    ts = pd.to_datetime(str(row["DateTime"]), format="%Y%m%d%H%M%S%f")
    bid_px = float(row["BidPrice1"])
    ask_px = float(row["AskPrice1"])
    bid_sz = float(row["BidVolume1"])
    ask_sz = float(row["AskVolume1"])

    if not _in_continuous_session(ts.to_pydatetime()):
        return "AUCTION_OR_NONCONTINUOUS"
    if bid_px <= 0 and ask_px <= 0:
        return "NO_QUOTE"
    if bid_px > 0 and ask_px > 0 and bid_sz > 0 and ask_sz > 0:
        return "EXECUTABLE"
    return "ONE_SIDED"


def load_legacy_workbook(path: Path, sheet_name: str | int | None = 0) -> pd.DataFrame:
    raw = pd.read_excel(path, sheet_name=sheet_name, header=None)
    if raw.shape[1] != len(LEGACY_COLUMN_ORDER):
        raise ValueError(
            f"unexpected legacy column width {raw.shape[1]}; expected {len(LEGACY_COLUMN_ORDER)}"
        )
    raw.columns = LEGACY_COLUMN_ORDER
    return raw


def prepare_legacy_snapshot(source_xlsx: Path, snapshot_csv: Path, master_csv: Path) -> PrepareReceipt:
    frame = load_legacy_workbook(source_xlsx)
    mo = frame[frame["SecurityID"].astype(str).str.startswith("MO", na=False)].copy()
    if mo.empty:
        raise ValueError("workbook contains no MO rows")

    mo["DerivedQuoteStatus"] = mo.apply(derive_quote_status, axis=1)
    status_counts = mo["DerivedQuoteStatus"].value_counts().astype(int).to_dict()

    sample_ts = pd.to_datetime(mo["DateTime"].astype(str).iloc[0], format="%Y%m%d%H%M%S%f")
    codes = sorted(mo["SecurityID"].astype(str).unique())
    master = pd.DataFrame(
        {
            "contract_code": codes,
            "expiry": [mo_expiry_from_contract_code(code) for code in codes],
        }
    )

    snapshot_csv.parent.mkdir(parents=True, exist_ok=True)
    mo.to_csv(snapshot_csv, index=False)
    master.to_csv(master_csv, index=False)

    return PrepareReceipt(
        prepare_id="rmr_R1B_MO_prepare_ciis_legacy_cff_snapshot_v1",
        source_xlsx=str(source_xlsx),
        snapshot_csv=str(snapshot_csv),
        contract_master_csv=str(master_csv),
        source_rows=len(frame),
        mo_rows=len(mo),
        contract_master_rows=len(master),
        sample_date=sample_ts.date().isoformat(),
        derived_quote_status_counts=status_counts,
        column_count=len(LEGACY_COLUMN_ORDER),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare CIIS legacy CFF Snapshot sample for MO adapter input.")
    parser.add_argument("--source-xlsx", required=True, type=Path)
    parser.add_argument("--snapshot-csv", required=True, type=Path)
    parser.add_argument("--contract-master-csv", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    receipt = prepare_legacy_snapshot(args.source_xlsx, args.snapshot_csv, args.contract_master_csv)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
