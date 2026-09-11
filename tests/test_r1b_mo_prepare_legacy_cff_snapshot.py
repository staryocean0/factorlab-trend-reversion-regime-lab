from __future__ import annotations

from pathlib import Path

import pandas as pd

from research.r1b_mo_data_admission.prepare_ciis_legacy_cff_snapshot import (
    derive_quote_status,
    load_legacy_workbook,
    mo_expiry_from_contract_code,
    prepare_legacy_snapshot,
)


def test_mo_expiry_uses_contract_month_third_friday():
    assert mo_expiry_from_contract_code("MO2302-C-6500") == "2023-02-17"


def test_derive_quote_status_marks_executable_two_sided_book():
    row = pd.Series(
        {
            "DateTime": "20221206093249400",
            "BidPrice1": 330.6,
            "BidVolume1": 7,
            "AskPrice1": 342.0,
            "AskVolume1": 12,
        }
    )
    assert derive_quote_status(row) == "EXECUTABLE"


def test_prepare_legacy_snapshot_from_headerless_fixture(tmp_path: Path):
    xlsx = tmp_path / "legacy.xlsx"
    rows = [
        [
            "MO2302-C-6500",
            20221206093249400,
            "SG01",
            1,
            334.4,
            334.0,
            334.4,
            116,
            0.0,
            0.0,
            0.0,
            0,
            0,
            334.4,
            116,
            0,
            0,
            1005.4,
            0.2,
            0,
            0,
            330.6,
            329.4,
            329.2,
            328.0,
            327.4,
            7,
            24,
            12,
            30,
            12,
            342.0,
            342.4,
            342.6,
            342.8,
            343.2,
            12,
            5,
            12,
            36,
            18,
        ],
        ["IM2301", 20221206093249400] + [0] * 39,
    ]
    pd.DataFrame(rows).to_excel(xlsx, index=False, header=False)

    snapshot = tmp_path / "Snapshot.csv"
    master = tmp_path / "master.csv"
    receipt = prepare_legacy_snapshot(xlsx, snapshot, master)

    assert receipt.mo_rows == 1
    assert receipt.contract_master_rows == 1
    assert receipt.empirical_option_outcome_test_authorized is False
    assert receipt.blackbox_query_count == 3

    loaded = load_legacy_workbook(xlsx)
    assert list(loaded.columns[:3]) == ["SecurityID", "DateTime", "SettlementGroupID"]

    out = pd.read_csv(snapshot)
    assert out.loc[0, "SecurityID"] == "MO2302-C-6500"
    assert out.loc[0, "DerivedQuoteStatus"] == "EXECUTABLE"
