"""Export admitted R1_A carrier minute tapes from the local DataHub lake.

Reads the pinned raw-canonical ETF partition already authorized for FactorLab
research. Does not fetch strategy-conditioned rows, impute prices, or choose
timestamp shifts by correlation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

DATASET_VERSION = "bars_cn_a_1m_raw_canonical_4ceca170a851"
LAKE_REL = (
    ".runtime/live/lake/bars/"
    f"dataset_version={DATASET_VERSION}/instrument_type=etf"
)
WINDOW = {"start": "2021-01-01", "end": "2025-12-31"}
YEARS = tuple(range(2021, 2026))

CARRIERS = {
    "512100.SH": {
        "lake_symbol": "512100",
        "source": "DataHub_local_lake_raw_canonical_1m",
        "source_reference": (
            "unified_datahub lake partition "
            f"{DATASET_VERSION}/instrument_type=etf; "
            "bar_align=session_end_label_v2; wall-clock Z suffix decoded as Asia/Shanghai"
        ),
        "corporate_actions_reference": (
            "Eastmoney pingzhong dividend ledger cross-checked with SSE cash-distribution "
            "notice 512100 ex-date 2025-01-15 "
            "(https://www.sse.com.cn/assortment/options/mnjyzxxx/c/c_20250115_10770107.shtml)"
        ),
        "actions": [
            {
                "symbol": "512100.SH",
                "ex_date": "2025-01-15",
                "event_type": "cash_distribution",
                "source_reference": (
                    "https://www.sse.com.cn/assortment/options/mnjyzxxx/c/c_20250115_10770107.shtml"
                ),
            }
        ],
    },
    "588000.SH": {
        "lake_symbol": "588000",
        "source": "DataHub_local_lake_raw_canonical_1m",
        "source_reference": (
            "unified_datahub lake partition "
            f"{DATASET_VERSION}/instrument_type=etf; "
            "bar_align=session_end_label_v2; wall-clock Z suffix decoded as Asia/Shanghai"
        ),
        "corporate_actions_reference": (
            "Eastmoney pingzhong dividend ledger 588000: only recorded split ex-date "
            "2020-11-09 precedes the frozen 2021-2025 window; no split/dividend rows "
            "inside 2021-01-01..2025-12-31 "
            "(https://fund.eastmoney.com/pingzhongdata/588000.js)"
        ),
        "actions": [],
    },
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _parse_datahub_wall_clock(values: pd.Series) -> pd.Series:
    text = values.astype(str)
    if bool(text.str.endswith("Z").all()):
        parsed = pd.to_datetime(text.str.removesuffix("Z"), errors="raise")
        return parsed.dt.tz_localize("Asia/Shanghai")
    parsed = pd.to_datetime(text, errors="raise")
    if parsed.dt.tz is None:
        return parsed.dt.tz_localize("Asia/Shanghai")
    return parsed.dt.tz_convert("Asia/Shanghai")


def _session_mask(index: pd.DatetimeIndex) -> pd.Series:
    clock = index.hour * 60 + index.minute
    return ((clock >= 570) & (clock <= 690)) | ((clock >= 781) & (clock <= 900))


def _load_year(lake_root: Path, lake_symbol: str, year: int) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for month in range(1, 13):
        month_key = f"{year}-{month:02d}"
        path = lake_root / f"trading_month={month_key}" / "data_0.parquet"
        if not path.is_file():
            continue
        frame = pd.read_parquet(path, filters=[("symbol", "=", lake_symbol)])
        if not frame.empty:
            parts.append(frame)
    if not parts:
        raise FileNotFoundError(f"no lake rows for {lake_symbol} in {year}")
    return pd.concat(parts, ignore_index=True)


def _to_canonical(frame: pd.DataFrame, carrier: str) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    if missing := sorted(required.difference(frame.columns)):
        raise ValueError(f"missing lake columns: {missing}")
    out = frame.copy()
    out["timestamp"] = _parse_datahub_wall_clock(out["timestamp"])
    out = out.loc[_session_mask(pd.DatetimeIndex(out["timestamp"]))].copy()
    days = out["timestamp"].dt.strftime("%Y-%m-%d")
    out = out.loc[(days >= WINDOW["start"]) & (days <= WINDOW["end"])].copy()
    for col in ("open", "high", "low", "close", "volume"):
        out[col] = pd.to_numeric(out[col], errors="raise")
    out["symbol"] = carrier
    out["timestamp"] = out["timestamp"].map(lambda ts: ts.isoformat())
    out = out[["symbol", "timestamp", "open", "high", "low", "close", "volume"]]
    out = out.sort_values("timestamp", kind="mergesort").drop_duplicates("timestamp", keep="last")
    if out.empty:
        raise ValueError(f"empty canonical export for {carrier}")
    if not out[["open", "high", "low", "close"]].gt(0).all().all():
        raise ValueError(f"nonpositive OHLC for {carrier}")
    if (out["volume"] < 0).any():
        raise ValueError(f"negative volume for {carrier}")
    return out.reset_index(drop=True)


def _file_spec(root: Path, rel_path: str, frame: pd.DataFrame) -> dict:
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return {
        "path": rel_path,
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "rows": len(frame),
    }


def export_carrier(
    repo_root: Path,
    datahub_root: Path,
    carrier: str,
    *,
    write_manifest: bool = True,
) -> dict:
    spec = CARRIERS[carrier]
    lake_root = datahub_root / LAKE_REL
    if not lake_root.is_dir():
        raise FileNotFoundError(f"DataHub ETF lake missing: {lake_root}")
    code = carrier.split(".")[0]
    files = []
    for year in YEARS:
        rel = f"data/r1a_carrier_prices/private/{code}_{year}.csv"
        canonical = _to_canonical(_load_year(lake_root, spec["lake_symbol"], year), carrier)
        year_days = canonical["timestamp"].str[:4]
        if not year_days.eq(str(year)).all():
            raise ValueError(f"{carrier} {year} export leaked other years")
        files.append(_file_spec(repo_root, rel, canonical))
    actions_rel = f"data/r1a_carrier_prices/private/{code}_actions.csv"
    actions = pd.DataFrame(spec["actions"], columns=["symbol", "ex_date", "event_type", "source_reference"])
    actions_file = _file_spec(repo_root, actions_rel, actions)
    manifest = {
        "symbol": carrier,
        "source": spec["source"],
        "source_reference": spec["source_reference"],
        "frequency": "1m",
        "timezone": "Asia/Shanghai",
        "bar_label": "bar_end",
        "price_basis": "unadjusted_actual_traded_OHLC",
        "volume_unit": "shares",
        "zero_volume_semantics": "not_an_observed_trade",
        "research_use_authorized": True,
        "corporate_actions_complete": True,
        "corporate_actions_reference": spec["corporate_actions_reference"],
        "corporate_actions_window": WINDOW,
        "files": files,
        "corporate_actions_file": actions_file,
        "dataset_version": DATASET_VERSION,
        "volume_note": "DataHub raw canonical 1m volume is exchange-reported share quantity",
    }
    receipt = {
        "carrier": carrier,
        "years": list(YEARS),
        "total_rows": sum(item["rows"] for item in files),
        "files": files,
        "corporate_actions_file": actions_file,
    }
    if write_manifest:
        manifest_path = repo_root / "data/r1a_carrier_prices" / f"{carrier}.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        receipt["manifest_path"] = str(manifest_path.relative_to(repo_root))
        receipt["manifest_sha256"] = _sha256(manifest_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument(
        "--datahub-root",
        type=Path,
        default=Path(__file__).resolve().parents[4] / "unified_datahub",
    )
    parser.add_argument("--output", type=Path, help="optional export receipt JSON")
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    datahub_root = args.datahub_root.resolve()
    receipts = {}
    for carrier in CARRIERS:
        receipts[carrier] = export_carrier(repo_root, datahub_root, carrier)
    payload = {
        "schema_id": "factorlab_r1a_carrier_datahub_export@1.0",
        "dataset_version": DATASET_VERSION,
        "window": WINDOW,
        "carriers": receipts,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: {"rows": v["total_rows"], "files": len(v["files"])} for k, v in receipts.items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
