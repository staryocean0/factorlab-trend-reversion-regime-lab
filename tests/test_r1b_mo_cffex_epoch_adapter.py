from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.r1b_mo_data_admission.adapt_cffex_snapshot_epochs import adapt_epochs


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _mapping(prefix: str) -> dict:
    return {
        "mapping_version": 1,
        "source_contract_code": f"{prefix}SecurityID",
        "source_timestamp": f"{prefix}DateTime",
        "timestamp_format": "%Y%m%d%H%M%S%f",
        "source_bid1": f"{prefix}Bid1",
        "source_bid1_size": f"{prefix}BidQty1",
        "source_ask1": f"{prefix}Ask1",
        "source_ask1_size": f"{prefix}AskQty1",
        "source_last_price": f"{prefix}Last",
        "source_volume": f"{prefix}Volume",
        "source_open_interest": f"{prefix}OI",
        "source_trading_status": f"{prefix}Phase",
        "trading_status_mapping": {"T": "TRADING"},
        "zero_quote_semantics": "synthetic fixture only: zero means unavailable quote",
        "source_timezone": "Asia/Shanghai",
        "master_contract_code": "contract_code",
        "master_expiry": "expiry",
    }


def _write_epoch(tmp_path: Path, prefix: str, code: str, timestamp: str, expiry: str):
    snapshot = tmp_path / f"{prefix}snapshot.csv"
    pd.DataFrame(
        [
            {
                f"{prefix}SecurityID": code,
                f"{prefix}DateTime": timestamp,
                f"{prefix}Bid1": 100.0,
                f"{prefix}BidQty1": 2,
                f"{prefix}Ask1": 101.0,
                f"{prefix}AskQty1": 3,
                f"{prefix}Last": 100.5,
                f"{prefix}Volume": 10,
                f"{prefix}OI": 100,
                f"{prefix}Phase": "T",
            }
        ]
    ).to_csv(snapshot, index=False)
    master = tmp_path / f"{prefix}master.csv"
    pd.DataFrame([{"contract_code": code, "expiry": expiry}]).to_csv(master, index=False)
    mapping = tmp_path / f"{prefix}mapping.json"
    _write_json(mapping, _mapping(prefix))
    return snapshot, master, mapping


def test_multi_epoch_adapter_keeps_distinct_physical_mappings(tmp_path: Path):
    legacy = _write_epoch(
        tmp_path,
        "L_",
        "MO2406-C-5000",
        "20240628093100400",
        "2024-07-19",
    )
    post = _write_epoch(
        tmp_path,
        "N_",
        "MO2409-P-5000",
        "20240708093100400",
        "2024-09-20",
    )

    manifest = tmp_path / "epochs.json"
    _write_json(
        manifest,
        {
            "epochs": [
                {
                    "epoch_id": "LEGACY_CFFEX_SNAPSHOT",
                    "snapshot": str(legacy[0]),
                    "contract_master": str(legacy[1]),
                    "mapping": str(legacy[2]),
                    "start": "2022-07-22",
                    "end": "2024-07-07",
                },
                {
                    "epoch_id": "POST_TRANSITION_CFFEX_DELIVERY",
                    "snapshot": str(post[0]),
                    "contract_master": str(post[1]),
                    "mapping": str(post[2]),
                    "start": "2024-07-08",
                    "end": "2026-09-10",
                },
            ]
        },
    )

    output, receipt = adapt_epochs(manifest)

    assert receipt.status == "MULTI_EPOCH_ADAPTED_NOT_ADMITTED"
    assert receipt.output_rows == 2
    assert receipt.admission_receipt_created is False
    assert receipt.empirical_option_outcome_test_authorized is False
    assert receipt.blackbox_query_count == 3
    assert receipt.production_authority is False
    assert set(output["source_epoch"]) == {
        "LEGACY_CFFEX_SNAPSHOT",
        "POST_TRANSITION_CFFEX_DELIVERY",
    }
    assert output["contract_code"].tolist() == ["MO2406-C-5000", "MO2409-P-5000"]


def test_multi_epoch_adapter_fails_if_one_mapping_is_unresolved(tmp_path: Path):
    legacy = _write_epoch(
        tmp_path,
        "L_",
        "MO2406-C-5000",
        "20240628093100400",
        "2024-07-19",
    )
    post = _write_epoch(
        tmp_path,
        "N_",
        "MO2409-P-5000",
        "20240708093100400",
        "2024-09-20",
    )
    bad_mapping = _mapping("N_")
    bad_mapping["source_ask1"] = ""
    _write_json(post[2], bad_mapping)

    manifest = tmp_path / "epochs.json"
    _write_json(
        manifest,
        {
            "epochs": [
                {
                    "epoch_id": "LEGACY_CFFEX_SNAPSHOT",
                    "snapshot": str(legacy[0]),
                    "contract_master": str(legacy[1]),
                    "mapping": str(legacy[2]),
                    "start": "2022-07-22",
                    "end": "2024-07-07",
                },
                {
                    "epoch_id": "POST_TRANSITION_CFFEX_DELIVERY",
                    "snapshot": str(post[0]),
                    "contract_master": str(post[1]),
                    "mapping": str(post[2]),
                    "start": "2024-07-08",
                    "end": "2026-09-10",
                },
            ]
        },
    )

    output, receipt = adapt_epochs(manifest)

    assert receipt.status == "FAIL_CLOSED"
    assert output.empty
    assert any("POST_TRANSITION_CFFEX_DELIVERY" in error for error in receipt.errors)


def test_multi_epoch_adapter_rejects_cross_epoch_timestamp_leakage(tmp_path: Path):
    legacy = _write_epoch(
        tmp_path,
        "L_",
        "MO2409-C-5000",
        "20240708093100400",
        "2024-09-20",
    )
    post = _write_epoch(
        tmp_path,
        "N_",
        "MO2409-P-5000",
        "20240708093100400",
        "2024-09-20",
    )

    manifest = tmp_path / "epochs.json"
    _write_json(
        manifest,
        {
            "epochs": [
                {
                    "epoch_id": "LEGACY_CFFEX_SNAPSHOT",
                    "snapshot": str(legacy[0]),
                    "contract_master": str(legacy[1]),
                    "mapping": str(legacy[2]),
                    "start": "2022-07-22",
                    "end": "2024-07-07",
                },
                {
                    "epoch_id": "POST_TRANSITION_CFFEX_DELIVERY",
                    "snapshot": str(post[0]),
                    "contract_master": str(post[1]),
                    "mapping": str(post[2]),
                    "start": "2024-07-08",
                    "end": "2026-09-10",
                },
            ]
        },
    )

    output, receipt = adapt_epochs(manifest)

    assert receipt.status == "FAIL_CLOSED"
    assert output.empty
    assert any("outside frozen bounds" in error for error in receipt.errors)
