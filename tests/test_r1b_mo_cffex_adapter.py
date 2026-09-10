from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.r1b_mo_data_admission.adapt_cffex_snapshot import adapt_snapshot


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _mapping() -> dict:
    return {
        "mapping_version": 1,
        "source_contract_code": "SecurityID",
        "source_timestamp": "DateTime",
        "timestamp_format": "%Y%m%d%H%M%S%f",
        "source_bid1": "BidPrice1",
        "source_bid1_size": "BidVolume1",
        "source_ask1": "AskPrice1",
        "source_ask1_size": "AskVolume1",
        "source_last_price": "LastPrice",
        "source_volume": "Volume",
        "source_open_interest": "OpenInterest",
        "source_trading_status": "Phase",
        "trading_status_mapping": {"T": "TRADING"},
        "zero_quote_semantics": "synthetic fixture only: zero means no executable quote",
        "source_timezone": "Asia/Shanghai",
        "master_contract_code": "contract_code",
        "master_expiry": "expiry",
    }


def test_adapter_maps_only_mo_rows_without_admission_authority(tmp_path: Path):
    snapshot = tmp_path / "Snapshot.csv"
    pd.DataFrame(
        [
            {
                "SecurityID": "MO2609-C-8000",
                "DateTime": "20260910093100400",
                "BidPrice1": 100.0,
                "BidVolume1": 3,
                "AskPrice1": 101.0,
                "AskVolume1": 4,
                "LastPrice": 100.6,
                "Volume": 10,
                "OpenInterest": 500,
                "Phase": "T",
            },
            {
                "SecurityID": "IM2609",
                "DateTime": "20260910093100400",
                "BidPrice1": 7000.0,
                "BidVolume1": 2,
                "AskPrice1": 7000.2,
                "AskVolume1": 2,
                "LastPrice": 7000.1,
                "Volume": 20,
                "OpenInterest": 1000,
                "Phase": "T",
            },
        ]
    ).to_csv(snapshot, index=False)

    master = tmp_path / "master.csv"
    pd.DataFrame([{"contract_code": "MO2609-C-8000", "expiry": "2026-09-18"}]).to_csv(master, index=False)

    mapping_path = tmp_path / "mapping.json"
    _write_json(mapping_path, _mapping())

    output, receipt = adapt_snapshot(snapshot, master, mapping_path)

    assert receipt.status == "ADAPTED_NOT_ADMITTED"
    assert receipt.source_rows == 2
    assert receipt.mo_rows == 1
    assert receipt.output_rows == 1
    assert receipt.admission_receipt_created is False
    assert receipt.empirical_option_outcome_test_authorized is False
    assert receipt.blackbox_query_count == 3
    assert receipt.production_authority is False
    assert output.loc[0, "contract_code"] == "MO2609-C-8000"
    assert output.loc[0, "option_type"] == "C"
    assert output.loc[0, "strike"] == 8000.0
    assert output.loc[0, "expiry"] == "2026-09-18"
    assert output.loc[0, "trading_status"] == "TRADING"


def test_adapter_rejects_unresolved_mapping_template(tmp_path: Path):
    snapshot = tmp_path / "Snapshot.csv"
    pd.DataFrame([{"SecurityID": "MO2609-C-8000"}]).to_csv(snapshot, index=False)
    master = tmp_path / "master.csv"
    pd.DataFrame([{"contract_code": "MO2609-C-8000", "expiry": "2026-09-18"}]).to_csv(master, index=False)

    mapping = _mapping()
    mapping["source_bid1"] = ""
    mapping["source_trading_status"] = ""
    mapping["trading_status_mapping"] = {}
    mapping["zero_quote_semantics"] = ""
    mapping_path = tmp_path / "mapping.json"
    _write_json(mapping_path, mapping)

    output, receipt = adapt_snapshot(snapshot, master, mapping_path)

    assert receipt.status == "FAIL_CLOSED"
    assert output.empty
    assert any("unresolved fields" in error for error in receipt.errors)
    assert receipt.empirical_option_outcome_test_authorized is False
    assert receipt.blackbox_query_count == 3


def test_adapter_rejects_unknown_status_value(tmp_path: Path):
    snapshot = tmp_path / "Snapshot.csv"
    pd.DataFrame(
        [
            {
                "SecurityID": "MO2609-P-8000",
                "DateTime": "20260910093100400",
                "BidPrice1": 88.0,
                "BidVolume1": 2,
                "AskPrice1": 89.0,
                "AskVolume1": 3,
                "LastPrice": 88.5,
                "Volume": 8,
                "OpenInterest": 420,
                "Phase": "UNKNOWN_SOURCE_CODE",
            }
        ]
    ).to_csv(snapshot, index=False)
    master = tmp_path / "master.csv"
    pd.DataFrame([{"contract_code": "MO2609-P-8000", "expiry": "2026-09-18"}]).to_csv(master, index=False)
    mapping_path = tmp_path / "mapping.json"
    _write_json(mapping_path, _mapping())

    output, receipt = adapt_snapshot(snapshot, master, mapping_path)

    assert receipt.status == "FAIL_CLOSED"
    assert output.empty
    assert any("unmapped trading_status" in error for error in receipt.errors)
