from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.r1b_mo_data_admission.adapt_datahub_mo_trade_activity import adapt_datahub_quotes


def _mapping() -> dict:
    return {
        "mapping_version": 1,
        "source_contract_code": "contract_symbol",
        "source_timestamp": "last_source_observed_at",
        "timestamp_format": "ISO8601_UTC_TO_ASIA_SHANGHAI",
        "source_bid1": "bid_price_1",
        "source_bid1_size": "bid_volume_1",
        "source_ask1": "ask_price_1",
        "source_ask1_size": "ask_volume_1",
        "source_last_price": "last_price",
        "source_volume": "trade_volume",
        "source_open_interest": "open_interest_last",
        "source_trading_status": "session_phase",
        "trading_status_mapping": {
            "continuous_am": "TRADING",
            "continuous_pm": "TRADING",
            "preopen": "AUCTION_OR_NONCONTINUOUS",
        },
        "zero_quote_semantics": "invalid bid/ask rows fail closed",
        "source_timezone": "Asia/Shanghai",
        "master_contract_code": "contract_symbol",
        "master_expiry": "expiry_date",
    }


def test_datahub_adapter_maps_mo_l1_rows_without_admission_authority(tmp_path: Path):
    quotes = tmp_path / "quotes.csv"
    pd.DataFrame(
        [
            {
                "contract_symbol": "MO2302-C-6500",
                "last_source_observed_at": "2022-12-06T01:32:49.400000+00:00",
                "bid_price_1": 330.6,
                "bid_volume_1": 7,
                "ask_price_1": 342.0,
                "ask_volume_1": 12,
                "last_price": 334.4,
                "trade_volume": 10,
                "open_interest_last": 116,
                "session_phase": "continuous_am",
                "source_kind": "baidu_cffex_500ms_derived_trade_activity_3s",
            }
        ]
    ).to_csv(quotes, index=False)

    master = tmp_path / "master.csv"
    pd.DataFrame([{"contract_symbol": "MO2302-C-6500", "expiry_date": "2023-02-17"}]).to_csv(master, index=False)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(_mapping()), encoding="utf-8")

    output, receipt = adapt_datahub_quotes(quotes, master, mapping_path)

    assert receipt.status == "ADAPTED_NOT_ADMITTED"
    assert receipt.output_rows == 1
    assert receipt.empirical_option_outcome_test_authorized is False
    assert output.loc[0, "contract_code"] == "MO2302-C-6500"
    assert output.loc[0, "timestamp"] == "2022-12-06 09:32:49.400000"
    assert output.loc[0, "trading_status"] == "TRADING"


def test_datahub_adapter_fails_on_invalid_bid_ask(tmp_path: Path):
    quotes = tmp_path / "quotes.csv"
    pd.DataFrame(
        [
            {
                "contract_symbol": "MO2302-C-6500",
                "last_source_observed_at": "2022-12-06T01:32:49.400000+00:00",
                "bid_price_1": 0.0,
                "bid_volume_1": 0,
                "ask_price_1": 342.0,
                "ask_volume_1": 12,
                "last_price": 334.4,
                "trade_volume": 10,
                "open_interest_last": 116,
                "session_phase": "continuous_am",
                "source_kind": "baidu_cffex_500ms_derived_trade_activity_3s",
            }
        ]
    ).to_csv(quotes, index=False)
    master = tmp_path / "master.csv"
    pd.DataFrame([{"contract_symbol": "MO2302-C-6500", "expiry_date": "2023-02-17"}]).to_csv(master, index=False)
    mapping_path = tmp_path / "mapping.json"
    mapping_path.write_text(json.dumps(_mapping()), encoding="utf-8")

    output, receipt = adapt_datahub_quotes(quotes, master, mapping_path)

    assert receipt.status == "FAIL_CLOSED"
    assert output.empty
