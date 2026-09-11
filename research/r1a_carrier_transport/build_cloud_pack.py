"""Build public cloud_pack_v1 from verified private CSV bytes.

Copies manifest-referenced private files byte-for-byte into a Git-tracked
directory. Does not re-export, impute, or alter OHLCV.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

PACK = "data/r1a_carrier_prices/cloud_pack_v1"
PRIVATE_MANIFESTS = (
    "data/r1a_carrier_prices/512100.SH.json",
    "data/r1a_carrier_prices/588000.SH.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_spec(root: Path, rel: str) -> dict:
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(rel)
    return {
        "path": rel,
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "rows": max(sum(1 for _ in path.open("rb")) - 1, 0),
    }


def build(root: Path) -> dict:
    pack = root / PACK
    prices = pack / "prices"
    prices.mkdir(parents=True, exist_ok=True)
    carriers: dict[str, dict] = {}
    for manifest_rel in PRIVATE_MANIFESTS:
        old = json.loads((root / manifest_rel).read_text(encoding="utf-8"))
        carrier = old["symbol"]
        copied_files = []
        for spec in old["files"]:
            src = root / spec["path"]
            name = Path(spec["path"]).name
            dst_rel = f"{PACK}/prices/{name}"
            dst = root / dst_rel
            if dst.exists() and sha256(dst) != spec["sha256"]:
                raise ValueError(f"existing cloud file hash drift: {dst_rel}")
            if not dst.exists():
                shutil.copyfile(src, dst)
            if sha256(dst) != spec["sha256"] or dst.stat().st_size != spec["bytes"]:
                raise ValueError(f"byte mismatch after copy: {dst_rel}")
            copied_files.append(file_spec(root, dst_rel))
        act_src = root / old["corporate_actions_file"]["path"]
        act_name = Path(old["corporate_actions_file"]["path"]).name
        act_rel = f"{PACK}/prices/{act_name}"
        act_dst = root / act_rel
        if not act_dst.exists():
            shutil.copyfile(act_src, act_dst)
        if sha256(act_dst) != old["corporate_actions_file"]["sha256"]:
            raise ValueError(f"actions byte mismatch: {act_rel}")
        actions = file_spec(root, act_rel)
        manifest = {
            k: old[k]
            for k in old
            if k not in {"files", "corporate_actions_file", "source_reference"}
        }
        manifest["source_reference"] = (
            old["source_reference"]
            + f"; public_redistribution_pack={PACK} copied from private delivery without transformation"
        )
        manifest["files"] = copied_files
        manifest["corporate_actions_file"] = actions
        manifest["delivery_pack"] = PACK
        manifest["private_manifest_sha256"] = sha256(root / manifest_rel)
        manifest_path = pack / f"{carrier}.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        carriers[carrier] = {
            "manifest_path": str(manifest_path.relative_to(root)),
            "manifest_sha256": sha256(manifest_path),
            "files": copied_files,
            "corporate_actions_file": actions,
            "total_rows": sum(x["rows"] for x in copied_files),
        }
    checklist = {
        "schema_id": "factorlab_r1a_cloud_pack_delivery_checklist@1.0",
        "pack": PACK,
        "carriers": carriers,
        "byte_identity": "private_to_cloud_pack_copyfile_no_rewrite",
    }
    (pack / "DELIVERY_CHECKLIST.json").write_text(
        json.dumps(checklist, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    readme = f"""# R1_A ETF public cloud pack v1

Git-tracked byte copies of the local private DataHub export (`b656b4b` lineage).
No OHLCV imputation, no zero-volume fill, no timestamp shift.

- Prices: `{PACK}/prices/*.csv`
- Manifests: `{PACK}/512100.SH.json`, `{PACK}/588000.SH.json`
- Checklist: `{PACK}/DELIVERY_CHECKLIST.json`

Cloud replay (does not change blocked primary admission):

```bash
PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py \\
  --manifest-dir {PACK} \\
  --output /tmp/r1a-cloud-replay-new
```

`512100.SH` may remain `INSUFFICIENT_CARRIER_MINUTE_COVERAGE` for 2021; that is
separate from whether these bytes are publicly readable.
"""
    (pack / "README.md").write_text(readme, encoding="utf-8")
    return checklist


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    receipt = build(root)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v["total_rows"] for k, v in receipt["carriers"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
