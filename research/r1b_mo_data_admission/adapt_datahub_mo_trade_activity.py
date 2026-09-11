#!/usr/bin/env python3
"""Map DataHub MO trade-activity rows to the frozen R1B canonical quote schema.

Source product: cffex_index_option_trade_activity_3s (L1 top-of-book in 3s buckets).
This is a licensed DataHub derivative feed, not a CFFEX/CIIS Level-2 snapshot file.
Adapter success remains ADAPTED_NOT_ADMITTED and does not authorize option outcomes.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from research.r1b_mo_data_admission.adapt_cffex_snapshot import (
    CANONICAL_COLUMNS,
    MappingError,
    _parse_contract_codes,
    _require_columns,
    _validate_mapping,
)

SERVING_SOURCE_KIND = "baidu_cffex_500ms_derived_trade_activity_3s"
NON_EXECUTABLE_SESSIONS = {"preopen", "postclose"}


@dataclass
class DataHubAdapterReceipt:
    adapter_id: str
    status: str
    quote_path: str
    contract_master_path: str
    mapping_path: str
    output_path: str
    source_rows: int
    mo_rows: int
    output_rows: int
    errors: list[str]
    warnings: list[str]
    admission_receipt_created: bool = False
    empirical_option_outcome_test_authorized: bool = False
    blackbox_query_count: int = 3
    production_authority: bool = False


def _load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise MappingError("mapping must be a JSON object")
    return obj


def _normalize_timestamps(series: pd.Series, source_timezone: str) -> pd.Series:
    ts = pd.to_datetime(series, utc=True, errors="coerce")
    if ts.isna().any():
        raise MappingError(f"timestamp parse failed rows={int(ts.isna().sum())}")
    if source_timezone != "Asia/Shanghai":
        raise MappingError("DataHub MO admission requires normalized Asia/Shanghai timestamps")
    return ts.dt.tz_convert("Asia/Shanghai")


def adapt_datahub_quotes(
    quote_path: Path,
    contract_master_path: Path,
    mapping_path: Path,
) -> tuple[pd.DataFrame, DataHubAdapterReceipt]:
    errors: list[str] = []
    warnings: list[str] = []
    output = pd.DataFrame(columns=CANONICAL_COLUMNS)

    try:
        mapping = _load_json(mapping_path)
        _validate_mapping(mapping)

        if quote_path.suffix.lower() == ".parquet":
            quotes = pd.read_parquet(quote_path)
        else:
            quotes = pd.read_csv(quote_path)

        master = pd.read_csv(contract_master_path, dtype={mapping["master_contract_code"]: "string"})

        source_cols = [
            mapping["source_contract_code"],
            mapping["source_timestamp"],
            mapping["source_bid1"],
            mapping["source_bid1_size"],
            mapping["source_ask1"],
            mapping["source_ask1_size"],
            mapping["source_last_price"],
            mapping["source_volume"],
            mapping["source_open_interest"],
            mapping["source_trading_status"],
        ]
        _require_columns(quotes, source_cols, "quotes")
        _require_columns(master, [mapping["master_contract_code"], mapping["master_expiry"]], "contract master")

        if "source_kind" in quotes.columns:
            kind = quotes["source_kind"].astype(str)
            allowed = kind == SERVING_SOURCE_KIND
            if not allowed.all():
                dropped = int((~allowed).sum())
                warnings.append(f"dropped non-serving source_kind rows={dropped}")
                quotes = quotes.loc[allowed].copy()

        contract_col = mapping["source_contract_code"]
        mo = quotes.loc[quotes[contract_col].astype(str).str.startswith("MO", na=False)].copy()
        if mo.empty:
            raise MappingError("quotes contain no MO contract rows")

        contract_code = mo[contract_col].astype(str)
        option_type, strike = _parse_contract_codes(contract_code)

        timestamps = _normalize_timestamps(mo[mapping["source_timestamp"]], mapping["source_timezone"])

        master_key = mapping["master_contract_code"]
        expiry_key = mapping["master_expiry"]
        master_slice = master[[master_key, expiry_key]].copy()
        if master_slice[master_key].duplicated().any():
            raise MappingError("contract master contains duplicate contract identifiers")
        expiry_map = master_slice.set_index(master_key)[expiry_key]
        expiries = contract_code.map(expiry_map)
        if expiries.isna().any():
            missing_codes = sorted(contract_code[expiries.isna()].unique().tolist())[:10]
            raise MappingError(f"contract master missing expiry for MO contracts: {missing_codes}")
        expiries = pd.to_datetime(expiries, errors="coerce")
        if expiries.isna().any():
            raise MappingError(f"contract master expiry parse failed rows={int(expiries.isna().sum())}")

        raw_status = mo[mapping["source_trading_status"]].astype(str)
        status_map = {str(k): str(v) for k, v in mapping["trading_status_mapping"].items()}
        normalized_status = raw_status.map(status_map)
        if normalized_status.isna().any():
            unknown = sorted(raw_status[normalized_status.isna()].unique().tolist())[:10]
            raise MappingError(f"unmapped trading_status values: {unknown}")

        bid1 = pd.to_numeric(mo[mapping["source_bid1"]], errors="coerce")
        ask1 = pd.to_numeric(mo[mapping["source_ask1"]], errors="coerce")
        bid1_size = pd.to_numeric(mo[mapping["source_bid1_size"]], errors="coerce")
        ask1_size = pd.to_numeric(mo[mapping["source_ask1_size"]], errors="coerce")
        invalid = (
            bid1.isna()
            | ask1.isna()
            | bid1_size.isna()
            | ask1_size.isna()
            | (bid1 <= 0)
            | (ask1 < bid1)
            | (bid1_size < 0)
            | (ask1_size < 0)
        )
        if invalid.any():
            dropped = int(invalid.sum())
            warnings.append(f"dropped serving-filter invalid bid/ask rows={dropped}")
            keep = ~invalid
            mo = mo.loc[keep].copy()
            contract_code = mo[contract_col].astype(str)
            option_type, strike = _parse_contract_codes(contract_code)
            timestamps = _normalize_timestamps(mo[mapping["source_timestamp"]], mapping["source_timezone"])
            expiries = pd.to_datetime(contract_code.map(expiry_map), errors="coerce")
            raw_status = mo[mapping["source_trading_status"]].astype(str)
            normalized_status = raw_status.map(status_map)
            bid1 = pd.to_numeric(mo[mapping["source_bid1"]], errors="coerce")
            ask1 = pd.to_numeric(mo[mapping["source_ask1"]], errors="coerce")
            bid1_size = pd.to_numeric(mo[mapping["source_bid1_size"]], errors="coerce")
            ask1_size = pd.to_numeric(mo[mapping["source_ask1_size"]], errors="coerce")
        if mo.empty:
            raise MappingError("no executable MO quote rows after serving filter")

        if raw_status.isin(NON_EXECUTABLE_SESSIONS).any():
            warnings.append(
                "rows include preopen/postclose session_phase; primary execution must exclude them downstream"
            )

        output = pd.DataFrame(
            {
                "contract_code": contract_code.values,
                "option_type": option_type.values,
                "strike": strike.values,
                "expiry": expiries.dt.strftime("%Y-%m-%d").values,
                "timestamp": timestamps.dt.strftime("%Y-%m-%d %H:%M:%S.%f").str.rstrip("0").str.rstrip(".").values,
                "bid1": bid1.values,
                "bid1_size": bid1_size.values,
                "ask1": ask1.values,
                "ask1_size": ask1_size.values,
                "last_price": mo[mapping["source_last_price"]].values,
                "volume": mo[mapping["source_volume"]].values,
                "open_interest": mo[mapping["source_open_interest"]].values,
                "trading_status": normalized_status.values,
            },
            columns=CANONICAL_COLUMNS,
        )

        receipt = DataHubAdapterReceipt(
            adapter_id="rmr_R1B_MO_datahub_trade_activity_adapter_v1",
            status="ADAPTED_NOT_ADMITTED",
            quote_path=str(quote_path),
            contract_master_path=str(contract_master_path),
            mapping_path=str(mapping_path),
            output_path="",
            source_rows=len(quotes),
            mo_rows=len(mo),
            output_rows=len(output),
            errors=errors,
            warnings=warnings,
        )
        return output, receipt
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
        receipt = DataHubAdapterReceipt(
            adapter_id="rmr_R1B_MO_datahub_trade_activity_adapter_v1",
            status="FAIL_CLOSED",
            quote_path=str(quote_path),
            contract_master_path=str(contract_master_path),
            mapping_path=str(mapping_path),
            output_path="",
            source_rows=0,
            mo_rows=0,
            output_rows=0,
            errors=errors,
            warnings=warnings,
        )
        return output, receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Map pinned DataHub MO trade-activity quotes to the frozen canonical schema. "
            "Never creates admission PASS or authorizes option outcomes."
        )
    )
    parser.add_argument("--quotes", required=True, type=Path)
    parser.add_argument("--contract-master", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    output, receipt = adapt_datahub_quotes(args.quotes, args.contract_master, args.mapping)
    receipt.output_path = str(args.output)

    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if receipt.status == "FAIL_CLOSED":
        print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
