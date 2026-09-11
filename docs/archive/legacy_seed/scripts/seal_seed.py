"""Freeze the public bootstrap surface; no literature ZIP is ever an input."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main():
    from regime_lab.package_guard import public_files

    output = ROOT / "docs/seed_manifest.json"
    files = []
    for path in public_files(ROOT):
        if path == output:
            continue
        with path.open("rb") as handle:
            digest = hashlib.file_digest(handle, "sha256").hexdigest()
        files.append({"path": str(path.relative_to(ROOT)), "sha256": digest, "bytes": path.stat().st_size})
    output.write_text(
        json.dumps(
            {
                "schema": "trend_reversion_public_seed@1.0",
                "files": files,
                "pdf_count": 0,
                "new_strategy_implemented": False,
                "empirical_research_executed": False,
                "old_strategy_results_imported": False,
                "local_storage_authoritative": True,
                "fresh_oos": False,
                "production_authority": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    print("sealed", len(files), "files; zero PDFs/archives")


if __name__ == "__main__":
    main()
