#!/usr/bin/env python3
"""Materialize full pinned DataHub MO window into canonical quote files + admission manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from research.r1b_mo_data_admission.adapt_datahub_mo_trade_activity import adapt_datahub_quotes
from research.r1b_mo_data_admission.export_datahub_mo_month import export_month
from research.r1b_mo_data_admission.validate_mo_quote_source import run as validate_admission

DEFAULT_BINDING = Path("docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json")
DEFAULT_MAPPING = Path("docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json")
DEFAULT_FEE = Path("docs/governance/R1B_MO_FEE_CONTRACT@1.0.json")


@dataclass
class MaterializeReceipt:
    materialize_id: str
    trading_months: int
    canonical_files: int
    total_output_rows: int
    manifest_path: str
    validator_status: str
    validator_receipt_path: str
    month_failures: list[str]
    blackbox_query_count: int = 3
    production_authority: bool = False
    empirical_option_outcome_test_authorized: bool = False


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _list_trading_months(binding_path: Path) -> list[str]:
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    root = Path(binding["dataset_binding"]["physical_path"]) / "activity" / "product_root=MO"
    return sorted(p.name.replace("trading_month=", "") for p in root.iterdir() if p.is_dir())


def _fee_manifest_block(fee_path: Path) -> dict:
    fee = json.loads(fee_path.read_text(encoding="utf-8"))
    return {
        "status": fee["status"],
        "exchange_fee_source": fee["exchange_fee_source"],
        "broker_fee_source": fee["broker_fee_source"],
        "frozen_as_of": fee["frozen_as_of"],
        "effective_periods": fee["effective_periods"],
    }


def _build_manifest(
    mapping_path: Path,
    fee_path: Path,
    file_entries: list[dict],
    routing_path: Path,
) -> dict:
    mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
    routing = json.loads(routing_path.read_text(encoding="utf-8"))
    return {
        "manifest_version": 1,
        "source_name": "DataHub cffex_index_option_trade_activity_3s MO L1",
        "source_type": "datahub_pinned_derivative_trade_activity_l1",
        "source_provenance_reference": str(DEFAULT_BINDING),
        "license_or_purchase_reference": routing["primary_source"]["binding"],
        "acquired_at": "2026-09-11T00:00:00+08:00",
        "quote_level": "L1",
        "contains_best_bid_ask": True,
        "source_timezone": "Asia/Shanghai",
        "timestamp_is_exchange_local": True,
        "volume_semantics": mapping.get(
            "volume_semantics",
            "trade_volume is the 3s bucket trade volume in contracts",
        ),
        "zero_quote_semantics": mapping.get(
            "zero_quote_semantics",
            "invalid bid/ask rows excluded by serving filter before canonicalization",
        ),
        "trading_status_mapping": mapping["trading_status_mapping"],
        "historical_window_start": routing["study_window"]["mo_quote_start"],
        "historical_window_end": routing["study_window"]["mo_quote_end_effective"],
        "historical_data_role": "reusable_instrument_development_evidence",
        "prospective_validation_boundary": "strictly_after_2026-08-25",
        "files": file_entries,
        "fee_contract": _fee_manifest_block(fee_path),
        "notes": (
            "Canonical monthly CSVs adapted from pinned DataHub MO trade-activity. "
            "Does not authorize option outcomes."
        ),
    }


def materialize(
    binding_path: Path,
    mapping_path: Path,
    fee_path: Path,
    routing_path: Path,
    quotes_dir: Path,
    manifest_path: Path,
    work_dir: Path,
) -> MaterializeReceipt:
    quotes_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    months = _list_trading_months(binding_path)
    file_entries: list[dict] = []
    month_failures: list[str] = []
    total_rows = 0

    first_work = work_dir / f"raw_{months[0]}"
    first_work.mkdir(parents=True, exist_ok=True)
    export_month(binding_path, months[0], first_work)
    master_path = work_dir / "contract_master.csv"
    exported_master = first_work / "contract_master.csv"
    if not exported_master.is_file():
        raise FileNotFoundError(f"missing contract master from export: {exported_master}")
    master_path.write_bytes(exported_master.read_bytes())

    for month in months:
        month_work = work_dir / f"raw_{month}"
        month_work.mkdir(parents=True, exist_ok=True)
        export_month(binding_path, month, month_work)
        quote_parquet = month_work / f"mo_quotes_{month}.parquet"
        out_csv = quotes_dir / f"mo_{month}.csv"
        output, receipt = adapt_datahub_quotes(quote_parquet, master_path, mapping_path)
        if receipt.status == "FAIL_CLOSED":
            month_failures.append(f"{month}: {receipt.errors}")
            continue
        output.to_csv(out_csv, index=False)
        rows = len(output)
        total_rows += rows
        file_entries.append(
            {
                "path": out_csv.name,
                "sha256": _sha256(out_csv),
                "size_bytes": out_csv.stat().st_size,
                "row_count": rows,
            }
        )

    manifest = _build_manifest(mapping_path, fee_path, file_entries, routing_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    validator_receipt_path = manifest_path.parent / "admission_validator_receipt.json"
    admission = validate_admission(quotes_dir, manifest_path)
    receipt_payload = json.dumps(asdict(admission), ensure_ascii=False, indent=2) + "\n"
    validator_receipt_path.write_text(receipt_payload, encoding="utf-8")
    evidence_receipt = Path("docs/ops/evidence/r1b_mo_admission_20260911/admission_validator_receipt.json")
    evidence_receipt.parent.mkdir(parents=True, exist_ok=True)
    evidence_receipt.write_text(receipt_payload, encoding="utf-8")

    return MaterializeReceipt(
        materialize_id="rmr_R1B_MO_materialize_datahub_admission_bundle_v1",
        trading_months=len(months),
        canonical_files=len(file_entries),
        total_output_rows=total_rows,
        manifest_path=str(manifest_path),
        validator_status=admission.status,
        validator_receipt_path=str(validator_receipt_path),
        month_failures=month_failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize full DataHub MO admission bundle and validate.")
    parser.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    parser.add_argument("--mapping", type=Path, default=DEFAULT_MAPPING)
    parser.add_argument("--fee", type=Path, default=DEFAULT_FEE)
    parser.add_argument(
        "--routing",
        type=Path,
        default=Path("docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json"),
    )
    parser.add_argument("--quotes-dir", type=Path, default=Path("data/r1b_mo_admission/datahub/quotes"))
    parser.add_argument("--manifest", type=Path, default=Path("data/r1b_mo_admission/datahub/manifest.json"))
    parser.add_argument("--work-dir", type=Path, default=Path("data/r1b_mo_admission/datahub/_work"))
    parser.add_argument(
        "--receipt",
        type=Path,
        default=Path("docs/ops/evidence/r1b_mo_admission_20260911/materialize_receipt.json"),
    )
    args = parser.parse_args()

    receipt = materialize(
        args.binding,
        args.mapping,
        args.fee,
        args.routing,
        args.quotes_dir,
        args.manifest,
        args.work_dir,
    )
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0 if receipt.validator_status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
