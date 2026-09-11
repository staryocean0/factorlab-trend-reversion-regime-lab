#!/usr/bin/env python3
"""Export one MO trading month from pinned DataHub lake paths for R1B schema work."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

DEFAULT_BINDING = Path("docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json")


@dataclass
class ExportReceipt:
    export_id: str
    trading_month: str
    quote_parquet: str
    contract_master_csv: str
    quote_rows: int
    master_rows: int
    blackbox_query_count: int = 3
    production_authority: bool = False


def export_month(binding_path: Path, trading_month: str, out_dir: Path) -> ExportReceipt:
    binding = json.loads(binding_path.read_text(encoding="utf-8"))
    ds = binding["dataset_binding"]
    activity_root = Path(ds["physical_path"]) / "activity" / "product_root=MO" / f"trading_month={trading_month}"
    parts = sorted(activity_root.glob("*.parquet"))
    if not parts:
        raise FileNotFoundError(f"no MO parquet partitions under {activity_root}")

    quotes = pd.concat([pd.read_parquet(p) for p in parts], ignore_index=True)
    identity = pd.read_parquet(ds["contract_identity_path"])
    mo_identity = identity.loc[identity["product_root"].astype(str) == "MO"].copy()
    master = mo_identity[["contract_symbol", "expiry_date"]].drop_duplicates("contract_symbol")

    out_dir.mkdir(parents=True, exist_ok=True)
    quote_out = out_dir / f"mo_quotes_{trading_month}.parquet"
    master_out = out_dir / "contract_master.csv"
    quotes.to_parquet(quote_out, index=False)
    master.to_csv(master_out, index=False)

    return ExportReceipt(
        export_id="rmr_R1B_MO_export_datahub_mo_month_v1",
        trading_month=trading_month,
        quote_parquet=str(quote_out),
        contract_master_csv=str(master_out),
        quote_rows=len(quotes),
        master_rows=len(master),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Export one pinned DataHub MO month for adapter validation.")
    parser.add_argument("--trading-month", required=True, help="YYYY-MM")
    parser.add_argument("--binding", type=Path, default=DEFAULT_BINDING)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    receipt = export_month(args.binding, args.trading_month, args.out_dir)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
