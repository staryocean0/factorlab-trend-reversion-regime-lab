"""Offline seed validation. Does not run any strategy, training or research."""

import hashlib
import importlib
import json
import sys
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]


def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main():
    from regime_lab.package_guard import public_files

    manifest = json.loads((ROOT / "docs/seed_manifest.json").read_text())
    current = {str(p.relative_to(ROOT)) for p in public_files(ROOT)} - {"docs/seed_manifest.json"}
    assert current == {r["path"] for r in manifest["files"]}, "unexpected or missing public seed files"
    for r in manifest["files"]:
        assert sha(ROOT / r["path"]) == r["sha256"], r["path"]
    infra = json.loads((ROOT / "docs/infrastructure_manifest.json").read_text())
    for r in infra["files"]:
        assert sha(ROOT / r["path"]) == r["sha256"]
        name = r["path"].removeprefix("src/").removesuffix(".py").replace("/", ".")
        module = importlib.import_module(name)
        assert Path(module.__file__).resolve() == (ROOT / r["path"]).resolve(), f"outside import {name}"
    data = json.loads((ROOT / "data/manifest.json").read_text())
    counts = {}
    for r in data["files"]:
        p = ROOT / r["path"]
        assert sha(p) == r["sha256"]
        f = pq.ParquetFile(p)
        assert f.metadata.num_rows == r["rows"]
        frame = f.read(columns=["symbol", "trading_day"]).to_pandas()
        assert set(frame.symbol) == {r["symbol"]} <= {"000688.SH", "000852.SH"}
        assert frame.trading_day.min() == r["first_day"] and frame.trading_day.max() == r["last_day"] <= "2025-12-31"
        key = r["symbol"] + ":" + r["frequency"]
        counts[key] = counts.get(key, 0) + len(frame)
    refs = json.loads((ROOT / "literature/references.json").read_text())
    assert len(refs) == 22 and all(not r["pdf_in_repository"] for r in refs)
    assert not manifest["new_strategy_implemented"] and not manifest["production_authority"]
    print(
        json.dumps(
            {
                "status": "passed",
                "files": len(manifest["files"]),
                "data_partitions": len(data["files"]),
                "data_rows": counts,
                "infrastructure_modules": len(infra["files"]),
                "literature_entries": 22,
                "pdf_files": 0,
                "empirical_research_executed": False,
                "production_authority": False,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
