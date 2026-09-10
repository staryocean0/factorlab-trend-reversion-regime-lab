#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = [
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

REQUIRED_MANIFEST_FIELDS = [
    "manifest_version",
    "source_name",
    "source_type",
    "source_provenance_reference",
    "license_or_purchase_reference",
    "acquired_at",
    "quote_level",
    "contains_best_bid_ask",
    "source_timezone",
    "timestamp_is_exchange_local",
    "volume_semantics",
    "zero_quote_semantics",
    "trading_status_mapping",
    "historical_window_start",
    "historical_window_end",
    "historical_data_role",
    "prospective_validation_boundary",
    "files",
    "fee_contract",
]

CONTRACT_RE = re.compile(r"^MO\d{4}-[CP]-\d+(?:\.\d+)?$")


@dataclass
class AdmissionReceipt:
    protocol_id: str
    status: str
    data_dir: str
    manifest_path: str
    rows_checked: int
    files_checked: int
    errors: list[str]
    warnings: list[str]
    empirical_option_outcome_test_authorized: bool = False
    blackbox_query_count: int = 3
    production_authority: bool = False


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix == ".csv":
        return pd.read_csv(path)
    raise ValueError(f"unsupported quote file type: {path.name}")


def require_manifest_fields(manifest: dict[str, Any], errors: list[str]) -> None:
    missing = [k for k in REQUIRED_MANIFEST_FIELDS if k not in manifest]
    if missing:
        errors.append(f"manifest missing required fields: {missing}")


def validate_manifest_semantics(manifest: dict[str, Any], errors: list[str]) -> None:
    if manifest.get("contains_best_bid_ask") is not True:
        errors.append("contains_best_bid_ask must be true")
    if manifest.get("source_timezone") != "Asia/Shanghai":
        errors.append("source_timezone must be Asia/Shanghai for admitted normalized tape")
    if manifest.get("timestamp_is_exchange_local") is not True:
        errors.append("timestamp_is_exchange_local must be true")
    if manifest.get("historical_data_role") != "reusable_instrument_development_evidence":
        errors.append("historical_data_role must be reusable_instrument_development_evidence")
    boundary = manifest.get("prospective_validation_boundary")
    if not isinstance(boundary, str) or not boundary.strip():
        errors.append("prospective_validation_boundary must be frozen and non-empty")
    if not isinstance(manifest.get("zero_quote_semantics"), str) or not manifest.get("zero_quote_semantics", "").strip():
        errors.append("zero_quote_semantics must be explicitly declared")
    mapping = manifest.get("trading_status_mapping")
    if not isinstance(mapping, dict) or not mapping:
        errors.append("trading_status_mapping must be a non-empty object")

    fee = manifest.get("fee_contract")
    if not isinstance(fee, dict):
        errors.append("fee_contract must be an object")
        return
    if fee.get("status") != "frozen":
        errors.append("fee_contract.status must equal frozen")
    for key in ["exchange_fee_source", "broker_fee_source", "frozen_as_of", "effective_periods"]:
        value = fee.get(key)
        if value in (None, "", [], {}):
            errors.append(f"fee_contract.{key} is required")


def validate_file_inventory(data_dir: Path, manifest: dict[str, Any], errors: list[str], warnings: list[str]) -> tuple[list[Path], int]:
    declared = manifest.get("files")
    if not isinstance(declared, list) or not declared:
        errors.append("manifest.files must be a non-empty list")
        return [], 0

    quote_files: list[Path] = []
    total_rows_declared = 0
    declared_paths: set[Path] = set()

    for item in declared:
        if not isinstance(item, dict):
            errors.append("each manifest.files entry must be an object")
            continue
        rel = item.get("path")
        if not isinstance(rel, str) or not rel:
            errors.append("file entry path is required")
            continue
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            errors.append(f"file path must be relative and contained: {rel}")
            continue
        path = data_dir / rel_path
        declared_paths.add(path.resolve())
        if not path.is_file():
            errors.append(f"declared file missing: {rel}")
            continue

        expected_sha = item.get("sha256")
        expected_size = item.get("size_bytes")
        expected_rows = item.get("row_count")
        if not isinstance(expected_sha, str) or len(expected_sha) != 64:
            errors.append(f"invalid sha256 declaration: {rel}")
        elif sha256_file(path) != expected_sha.lower():
            errors.append(f"sha256 mismatch: {rel}")
        if not isinstance(expected_size, int) or expected_size < 0:
            errors.append(f"invalid size_bytes declaration: {rel}")
        elif path.stat().st_size != expected_size:
            errors.append(f"size_bytes mismatch: {rel}")
        if not isinstance(expected_rows, int) or expected_rows < 0:
            errors.append(f"invalid row_count declaration: {rel}")
        else:
            total_rows_declared += expected_rows

        if path.suffix.lower() in {".parquet", ".csv"}:
            quote_files.append(path)
        else:
            warnings.append(f"non-tabular declared file ignored for row validation: {rel}")

    actual_quote_files = {
        p.resolve()
        for p in data_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in {".parquet", ".csv"}
    }
    undeclared = sorted(str(p.relative_to(data_dir.resolve())) for p in actual_quote_files - declared_paths)
    if undeclared:
        errors.append(f"undeclared quote files present: {undeclared}")

    return quote_files, total_rows_declared


def validate_quotes(frame: pd.DataFrame, source_name: str, errors: list[str]) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        errors.append(f"{source_name}: missing canonical columns: {missing}")
        return

    if frame.empty:
        errors.append(f"{source_name}: quote table is empty")
        return

    codes = frame["contract_code"].astype(str)
    bad_codes = ~codes.str.match(CONTRACT_RE)
    if bad_codes.any():
        errors.append(f"{source_name}: invalid MO contract_code rows={int(bad_codes.sum())}")

    option_types = frame["option_type"].astype(str).str.upper()
    bad_types = ~option_types.isin(["C", "P"])
    if bad_types.any():
        errors.append(f"{source_name}: option_type must be C/P rows={int(bad_types.sum())}")

    numeric_cols = ["strike", "bid1", "bid1_size", "ask1", "ask1_size", "last_price", "volume", "open_interest"]
    numeric = {}
    for col in numeric_cols:
        numeric[col] = pd.to_numeric(frame[col], errors="coerce")
        if numeric[col].isna().any():
            errors.append(f"{source_name}: non-numeric/null {col} rows={int(numeric[col].isna().sum())}")

    if numeric["strike"].notna().any() and (numeric["strike"] <= 0).any():
        errors.append(f"{source_name}: strike must be >0")
    for col in ["bid1", "bid1_size", "ask1", "ask1_size", "last_price", "volume", "open_interest"]:
        if numeric[col].notna().any() and (numeric[col] < 0).any():
            errors.append(f"{source_name}: {col} must be >=0")

    crossed = (numeric["bid1"] > 0) & (numeric["ask1"] > 0) & (numeric["bid1"] > numeric["ask1"])
    if crossed.any():
        errors.append(f"{source_name}: crossed positive best quotes rows={int(crossed.sum())}")

    timestamps = pd.to_datetime(frame["timestamp"], errors="coerce")
    expiries = pd.to_datetime(frame["expiry"], errors="coerce")
    if timestamps.isna().any():
        errors.append(f"{source_name}: invalid timestamp rows={int(timestamps.isna().sum())}")
    if expiries.isna().any():
        errors.append(f"{source_name}: invalid expiry rows={int(expiries.isna().sum())}")
    valid_pair = timestamps.notna() & expiries.notna()
    if valid_pair.any() and (expiries[valid_pair].dt.date < timestamps[valid_pair].dt.date).any():
        errors.append(f"{source_name}: expiry precedes quote date")

    dup = frame.duplicated(["contract_code", "timestamp"], keep=False)
    if dup.any():
        errors.append(f"{source_name}: duplicate contract_code/timestamp rows={int(dup.sum())}")

    if frame["trading_status"].isna().any():
        errors.append(f"{source_name}: null trading_status rows={int(frame['trading_status'].isna().sum())}")


def run(data_dir: Path, manifest_path: Path) -> AdmissionReceipt:
    errors: list[str] = []
    warnings: list[str] = []
    rows_checked = 0
    files_checked = 0

    if not manifest_path.is_file():
        errors.append("manifest file does not exist")
        return AdmissionReceipt(
            protocol_id="rmr_R1B_MO_data_admission_v1",
            status="FAIL",
            data_dir=str(data_dir),
            manifest_path=str(manifest_path),
            rows_checked=0,
            files_checked=0,
            errors=errors,
            warnings=warnings,
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    require_manifest_fields(manifest, errors)
    validate_manifest_semantics(manifest, errors)
    quote_files, declared_rows = validate_file_inventory(data_dir, manifest, errors, warnings)

    for path in quote_files:
        try:
            frame = load_table(path)
        except Exception as exc:  # admission receipt must preserve loader failure
            errors.append(f"{path.name}: load failed: {type(exc).__name__}: {exc}")
            continue
        files_checked += 1
        rows_checked += len(frame)
        validate_quotes(frame, str(path.relative_to(data_dir)), errors)

    if quote_files and rows_checked != declared_rows:
        errors.append(f"declared row_count total={declared_rows} actual={rows_checked}")

    return AdmissionReceipt(
        protocol_id="rmr_R1B_MO_data_admission_v1",
        status="PASS" if not errors else "FAIL",
        data_dir=str(data_dir),
        manifest_path=str(manifest_path),
        rows_checked=rows_checked,
        files_checked=files_checked,
        errors=errors,
        warnings=warnings,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an MO historical best-bid/best-ask source without opening option outcomes.")
    parser.add_argument("--data-dir", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()

    receipt = run(args.data_dir, args.manifest)
    payload = json.dumps(asdict(receipt), ensure_ascii=False, indent=2, sort_keys=True)
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if receipt.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
