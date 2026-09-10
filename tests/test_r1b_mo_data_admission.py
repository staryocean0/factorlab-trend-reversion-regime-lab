from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

from research.r1b_mo_data_admission.validate_mo_quote_source import run


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "contract_code": "MO2609-C-8000",
                "option_type": "C",
                "strike": 8000,
                "expiry": "2026-09-18",
                "timestamp": "2026-09-10 09:31:00",
                "bid1": 100.0,
                "bid1_size": 3,
                "ask1": 101.0,
                "ask1_size": 4,
                "last_price": 100.6,
                "volume": 10,
                "open_interest": 500,
                "trading_status": "TRADING",
            },
            {
                "contract_code": "MO2609-P-8000",
                "option_type": "P",
                "strike": 8000,
                "expiry": "2026-09-18",
                "timestamp": "2026-09-10 09:31:00",
                "bid1": 88.0,
                "bid1_size": 2,
                "ask1": 89.2,
                "ask1_size": 5,
                "last_price": 88.6,
                "volume": 8,
                "open_interest": 420,
                "trading_status": "TRADING",
            },
        ]
    )


def _manifest(path: Path, rows: int) -> dict:
    return {
        "manifest_version": 1,
        "source_name": "synthetic_test_only",
        "source_type": "unit_test_fixture",
        "source_provenance_reference": "tests-only",
        "license_or_purchase_reference": "tests-only",
        "acquired_at": "2026-09-10T00:00:00+08:00",
        "quote_level": "L1",
        "contains_best_bid_ask": True,
        "source_timezone": "Asia/Shanghai",
        "timestamp_is_exchange_local": True,
        "volume_semantics": "cumulative_or_source_declared_test_fixture",
        "zero_quote_semantics": "zero means no executable quote in test fixture",
        "trading_status_mapping": {"TRADING": "valid_continuous"},
        "historical_window_start": "2026-09-10",
        "historical_window_end": "2026-09-10",
        "historical_data_role": "reusable_instrument_development_evidence",
        "prospective_validation_boundary": "strictly_after_2026-09-10",
        "files": [
            {
                "path": path.name,
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
                "row_count": rows,
            }
        ],
        "fee_contract": {
            "status": "frozen",
            "exchange_fee_source": "synthetic-test-source",
            "broker_fee_source": "synthetic-test-source",
            "frozen_as_of": "2026-09-10",
            "effective_periods": [{"start": "2026-01-01", "end": None, "rule": "synthetic-only"}],
        },
    }


def _write_case(tmp_path: Path, frame: pd.DataFrame, mutate_manifest=None):
    data_dir = tmp_path / "quotes"
    data_dir.mkdir()
    quote_path = data_dir / "mo_quotes.csv"
    frame.to_csv(quote_path, index=False)
    manifest = _manifest(quote_path, len(frame))
    if mutate_manifest:
        mutate_manifest(manifest)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return data_dir, manifest_path


def test_valid_synthetic_source_passes(tmp_path: Path):
    data_dir, manifest_path = _write_case(tmp_path, _frame())
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "PASS"
    assert receipt.rows_checked == 2
    assert receipt.files_checked == 1
    assert receipt.empirical_option_outcome_test_authorized is False
    assert receipt.blackbox_query_count == 3
    assert receipt.production_authority is False


def test_missing_best_ask_column_fails(tmp_path: Path):
    frame = _frame().drop(columns=["ask1"])
    data_dir, manifest_path = _write_case(tmp_path, frame)
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "FAIL"
    assert any("missing canonical columns" in error for error in receipt.errors)


def test_crossed_quote_fails(tmp_path: Path):
    frame = _frame()
    frame.loc[0, "bid1"] = 102.0
    frame.loc[0, "ask1"] = 101.0
    data_dir, manifest_path = _write_case(tmp_path, frame)
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "FAIL"
    assert any("crossed positive best quotes" in error for error in receipt.errors)


def test_unfrozen_fee_contract_fails(tmp_path: Path):
    def mutate(manifest: dict):
        manifest["fee_contract"]["status"] = "pending"

    data_dir, manifest_path = _write_case(tmp_path, _frame(), mutate)
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "FAIL"
    assert any("fee_contract.status" in error for error in receipt.errors)


def test_checksum_mismatch_fails(tmp_path: Path):
    def mutate(manifest: dict):
        manifest["files"][0]["sha256"] = "0" * 64

    data_dir, manifest_path = _write_case(tmp_path, _frame(), mutate)
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "FAIL"
    assert any("sha256 mismatch" in error for error in receipt.errors)


def test_undeclared_quote_file_fails(tmp_path: Path):
    data_dir, manifest_path = _write_case(tmp_path, _frame())
    _frame().to_csv(data_dir / "undeclared.csv", index=False)
    receipt = run(data_dir, manifest_path)
    assert receipt.status == "FAIL"
    assert any("undeclared quote files" in error for error in receipt.errors)
