"""Verify public cloud_pack_v1 bytes are present and match private lineage."""
import hashlib
import json
from pathlib import Path

import pytest

from research.r1a_carrier_transport.transport import admit, WINDOW

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "data/r1a_carrier_prices/cloud_pack_v1"
PRIVATE = ROOT / "data/r1a_carrier_prices"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@pytest.mark.parametrize("carrier", ["512100.SH", "588000.SH"])
def test_cloud_pack_manifest_files_exist_and_match_private_hashes(carrier: str):
    private = json.loads((PRIVATE / f"{carrier}.json").read_text(encoding="utf-8"))
    public = json.loads((PACK / f"{carrier}.json").read_text(encoding="utf-8"))
    assert public["symbol"] == carrier
    assert public["bar_label"] == "bar_end"
    assert public["research_use_authorized"] is True
    for priv, pub in zip(private["files"], public["files"], strict=True):
        assert Path(pub["path"]).name == Path(priv["path"]).name
        assert pub["sha256"] == priv["sha256"]
        assert pub["bytes"] == priv["bytes"]
        assert pub["rows"] == priv["rows"]
        path = ROOT / pub["path"]
        assert path.is_file(), pub["path"]
        assert sha256(path) == pub["sha256"]
    priv_a = private["corporate_actions_file"]
    pub_a = public["corporate_actions_file"]
    assert pub_a["sha256"] == priv_a["sha256"]
    assert (ROOT / pub_a["path"]).is_file()


def test_cloud_pack_checklist_lists_all_price_files():
    checklist = json.loads((PACK / "DELIVERY_CHECKLIST.json").read_text(encoding="utf-8"))
    assert checklist["pack"] == "data/r1a_carrier_prices/cloud_pack_v1"
    for carrier in ("512100.SH", "588000.SH"):
        info = checklist["carriers"][carrier]
        assert info["total_rows"] > 200_000
        assert len(info["files"]) == 5


def test_cloud_pack_512100_still_fails_2021_gate_without_private():
    from regime_lab.market_data import load_market_data
    import pandas as pd

    manifest = PACK / "512100.SH.json"
    index = load_market_data("000852.SH", "1m", "2021-01-01", "2025-12-31", root=ROOT)
    times = pd.DatetimeIndex(index.market_time_shanghai)
    with pytest.raises(Exception, match="INSUFFICIENT_CARRIER_MINUTE_COVERAGE"):
        admit(ROOT, manifest, "512100.SH", times)


def test_cloud_pack_588000_passes_admission_without_private():
    from regime_lab.market_data import load_market_data
    import pandas as pd

    manifest = PACK / "588000.SH.json"
    index = load_market_data("000688.SH", "1m", "2020-07-23", "2025-12-31", root=ROOT)
    times = pd.DatetimeIndex(index.market_time_shanghai)
    tape, actions, receipt = admit(ROOT, manifest, "588000.SH", times)
    assert receipt["status"] == "PASS_DATA_ADMISSION_ONLY"
    assert len(tape) > 200_000
