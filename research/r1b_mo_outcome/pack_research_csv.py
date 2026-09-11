#!/usr/bin/env python3
"""Build the in-repo CSV research pack for cloud execution.

GitHub rejects files over 100MB, so monthly MO L1 is slimmed to the frozen
quote columns and split by day when a month would exceed 80MB. 2026 MO rows
are omitted because the admitted 000852.SH 1m series ends 2025-12-31.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from regime_lab.market_data import load_market_data
from research.r1b_mo_outcome.quotes import QUOTE_COLUMNS

MAX_FILE_BYTES = 80 * 1024 * 1024
JOINABLE_START = "2022-07"
JOINABLE_END = "2025-12"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def pack_underlying(repo: Path, dest_dir: Path) -> list[dict]:
    frame = load_market_data("000852.SH", "1m", "2015-01-05", "2025-12-31", root=repo)
    cols = [col for col in ("symbol", "trading_day", "timestamp", "open", "high", "low", "close") if col in frame.columns]
    entries = []
    dest_dir.mkdir(parents=True, exist_ok=True)
    for year, part in frame.groupby(frame["trading_day"].astype(str).str[:4], sort=True):
        path = dest_dir / f"000852.SH_1m_{year}.csv"
        _write_csv(path, part[cols])
        entries.append(
            {
                "path": str(path.relative_to(repo)),
                "kind": "underlying_1m",
                "symbol": "000852.SH",
                "year": str(year),
                "rows": int(len(part)),
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return entries


def pack_quotes(source_dir: Path, dest_dir: Path, repo: Path) -> tuple[list[dict], list[dict]]:
    dest_dir.mkdir(parents=True, exist_ok=True)
    master_frames = []
    file_entries = []
    sources = sorted(source_dir.glob("mo_*.csv"))
    for src in sources:
        month = src.stem.replace("mo_", "")
        if month < JOINABLE_START or month > JOINABLE_END:
            continue
        print(f"packing {month}", flush=True)
        frame = pd.read_csv(src, usecols=QUOTE_COLUMNS)
        master_frames.append(frame[["contract_code", "option_type", "strike", "expiry"]].drop_duplicates("contract_code"))
        encoded = frame.to_csv(index=False).encode()
        if len(encoded) <= MAX_FILE_BYTES:
            path = dest_dir / f"mo_{month}.csv"
            path.write_bytes(encoded)
            written = [path]
        else:
            days = pd.to_datetime(frame["timestamp"]).dt.strftime("%Y-%m-%d")
            written = []
            for day, part in frame.groupby(days, sort=True):
                path = dest_dir / f"mo_{day}.csv"
                _write_csv(path, part[QUOTE_COLUMNS])
                if path.stat().st_size > MAX_FILE_BYTES:
                    raise RuntimeError(f"{path} still exceeds {MAX_FILE_BYTES} bytes")
                written.append(path)
        for path in written:
            file_entries.append(
                {
                    "path": str(path.relative_to(repo)),
                    "kind": "mo_l1_quote",
                    "month": month,
                    "rows": int(sum(1 for _ in path.open(encoding="utf-8")) - 1),
                    "sha256": sha256_file(path),
                    "size_bytes": path.stat().st_size,
                }
            )
    if not master_frames:
        raise RuntimeError("no joinable MO quote months found")
    master = pd.concat(master_frames, ignore_index=True).drop_duplicates("contract_code", keep="first")
    master = master.sort_values("contract_code").reset_index(drop=True)
    master_path = dest_dir.parent / "contract_master.csv"
    _write_csv(master_path, master)
    master_entry = {
        "path": str(master_path.relative_to(repo)),
        "kind": "contract_master",
        "rows": int(len(master)),
        "sha256": sha256_file(master_path),
        "size_bytes": master_path.stat().st_size,
    }
    return file_entries, [master_entry]


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack research CSVs for in-repo cloud execution.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--source-quotes", type=Path, default=Path("data/r1b_mo_admission/datahub/quotes"))
    parser.add_argument("--dest", type=Path, default=Path("data/r1b_research"))
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    dest = args.dest if args.dest.is_absolute() else repo / args.dest
    source = args.source_quotes if args.source_quotes.is_absolute() else repo / args.source_quotes
    underlying_entries = pack_underlying(repo, dest / "underlying_1m")
    quote_entries, master_entries = pack_quotes(source, dest / "mo_quotes", repo)
    manifest = {
        "schema": "r1b_research_csv_pack@1.0",
        "joinable_quote_window": {"start": "2022-07-22", "end": "2025-12-31"},
        "underlying": {"symbol": "000852.SH", "frequency": "1m", "start": "2015-01-05", "end": "2025-12-31"},
        "year_2026_mo_omitted": "unjoinable_without_admitted_2026_1m",
        "max_file_bytes": MAX_FILE_BYTES,
        "files": underlying_entries + master_entries + quote_entries,
    }
    manifest_path = dest / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(manifest["files"]), "dest": str(dest)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
