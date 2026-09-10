#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

MO_RE = re.compile(r"^(MO\d{4})-([CP])-(\d+(?:\.\d+)?)$")

REQUIRED_MAPPING_KEYS = [
    "mapping_version",
    "source_contract_code",
    "source_timestamp",
    "timestamp_format",
    "source_bid1",
    "source_bid1_size",
    "source_ask1",
    "source_ask1_size",
    "source_last_price",
    "source_volume",
    "source_open_interest",
    "source_trading_status",
    "trading_status_mapping",
    "zero_quote_semantics",
    "source_timezone",
    "master_contract_code",
    "master_expiry",
]

CANONICAL_COLUMNS = [
    "contract_code",
    "option_type",
    "strike",
    "expiry",
    "timestamp",
    "bid1",
    "bid1_size",
    "ask1",
    "ask1_size",
    "last_price",
    "volume",
    "open_interest",
    "trading_status",
]


class MappingError(ValueError):
    pass


@dataclass
class AdapterReceipt:
    adapter_id: str
    status: str
    snapshot_path: str
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


def _validate_mapping(mapping: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_MAPPING_KEYS if key not in mapping]
    if missing:
        raise MappingError(f"mapping missing required keys: {missing}")

    unresolved = []
    scalar_fields = [
        "source_contract_code",
        "source_timestamp",
        "timestamp_format",
        "source_bid1",
        "source_bid1_size",
        "source_ask1",
        "source_ask1_size",
        "source_last_price",
        "source_volume",
        "source_open_interest",
        "source_trading_status",
        "zero_quote_semantics",
        "source_timezone",
        "master_contract_code",
        "master_expiry",
    ]
    for key in scalar_fields:
        value = mapping.get(key)
        if not isinstance(value, str) or not value.strip():
            unresolved.append(key)
    if unresolved:
        raise MappingError(
            "mapping contains unresolved fields; fill only from the delivered dictionary/sample before use: "
            + ", ".join(unresolved)
        )

    if mapping["source_timezone"] != "Asia/Shanghai":
        raise MappingError("source_timezone must be explicitly verified as Asia/Shanghai")

    status_map = mapping.get("trading_status_mapping")
    if not isinstance(status_map, dict) or not status_map:
        raise MappingError("trading_status_mapping must be a non-empty object based on source documentation")


def _require_columns(frame: pd.DataFrame, columns: list[str], source: str) -> None:
    missing = [col for col in columns if col not in frame.columns]
    if missing:
        raise MappingError(f"{source} missing mapped columns: {missing}")


def _parse_contract_codes(codes: pd.Series) -> tuple[pd.Series, pd.Series]:
    option_type: list[str] = []
    strike: list[float] = []
    bad: list[str] = []
    for code in codes.astype(str):
        match = MO_RE.fullmatch(code)
        if not match:
            bad.append(code)
            option_type.append("")
            strike.append(float("nan"))
            continue
        option_type.append(match.group(2))
        strike.append(float(match.group(3)))
    if bad:
        sample = sorted(set(bad))[:5]
        raise MappingError(
            f"MO SecurityID/contract identity does not match frozen CFFEX code grammar; rows={len(bad)} sample={sample}"
        )
    return pd.Series(option_type, index=codes.index), pd.Series(strike, index=codes.index)


def adapt_snapshot(
    snapshot_path: Path,
    contract_master_path: Path,
    mapping_path: Path,
) -> tuple[pd.DataFrame, AdapterReceipt]:
    errors: list[str] = []
    warnings: list[str] = []
    output = pd.DataFrame(columns=CANONICAL_COLUMNS)

    try:
        mapping = _load_json(mapping_path)
        _validate_mapping(mapping)
        raw = pd.read_csv(snapshot_path, dtype={mapping["source_contract_code"]: "string"})
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
        _require_columns(raw, source_cols, "snapshot")
        _require_columns(master, [mapping["master_contract_code"], mapping["master_expiry"]], "contract master")

        source_codes = raw[mapping["source_contract_code"]].astype("string")
        mo_mask = source_codes.str.startswith("MO", na=False)
        mo = raw.loc[mo_mask].copy()
        if mo.empty:
            raise MappingError("snapshot contains no rows whose source contract code begins with MO")

        contract_code = mo[mapping["source_contract_code"]].astype(str)
        option_type, strike = _parse_contract_codes(contract_code)

        timestamps = pd.to_datetime(
            mo[mapping["source_timestamp"]].astype(str),
            format=mapping["timestamp_format"],
            errors="coerce",
        )
        if timestamps.isna().any():
            raise MappingError(f"timestamp parse failed rows={int(timestamps.isna().sum())}")

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

        output = pd.DataFrame(
            {
                "contract_code": contract_code.values,
                "option_type": option_type.values,
                "strike": strike.values,
                "expiry": expiries.dt.strftime("%Y-%m-%d").values,
                "timestamp": timestamps.dt.strftime("%Y-%m-%d %H:%M:%S.%f").str.rstrip("0").str.rstrip(".").values,
                "bid1": mo[mapping["source_bid1"]].values,
                "bid1_size": mo[mapping["source_bid1_size"]].values,
                "ask1": mo[mapping["source_ask1"]].values,
                "ask1_size": mo[mapping["source_ask1_size"]].values,
                "last_price": mo[mapping["source_last_price"]].values,
                "volume": mo[mapping["source_volume"]].values,
                "open_interest": mo[mapping["source_open_interest"]].values,
                "trading_status": normalized_status.values,
            },
            columns=CANONICAL_COLUMNS,
        )

        receipt = AdapterReceipt(
            adapter_id="rmr_R1B_MO_cffex_snapshot_adapter_v1",
            status="ADAPTED_NOT_ADMITTED",
            snapshot_path=str(snapshot_path),
            contract_master_path=str(contract_master_path),
            mapping_path=str(mapping_path),
            output_path="",
            source_rows=len(raw),
            mo_rows=len(mo),
            output_rows=len(output),
            errors=errors,
            warnings=warnings,
        )
        return output, receipt
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
        receipt = AdapterReceipt(
            adapter_id="rmr_R1B_MO_cffex_snapshot_adapter_v1",
            status="FAIL_CLOSED",
            snapshot_path=str(snapshot_path),
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
            "Map a documented CFFEX/CIIS Snapshot CSV to the frozen MO canonical schema. "
            "This is a source-schema adapter only and never creates an admission PASS or authorizes option outcomes."
        )
    )
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--contract-master", required=True, type=Path)
    parser.add_argument("--mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    output, receipt = adapt_snapshot(args.snapshot, args.contract_master, args.mapping)
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
