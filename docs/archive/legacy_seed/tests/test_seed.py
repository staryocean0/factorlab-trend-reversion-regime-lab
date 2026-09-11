import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from factor_lab.data.services.standard_backtest_service import resolve_execution_window
from factor_lab.data.session_offset_defaults import assert_no_local_bar_resample, default_data_contract
from factor_lab.governance.multiple_testing import evaluate_benjamini_hochberg
from factor_lab.market_state.normalization import empirical_location
from regime_lab.market_data import load_market_data, validate_request
from regime_lab.package_guard import public_files


@pytest.mark.parametrize(
    "symbol,freq,start,end",
    [
        ("588000.SSE", "1m", "2024-01-02", "2024-01-03"),
        ("000852.SH", "1m", "2014-10-17", "2014-10-20"),
        ("000688.SH", "3s", "2020-07-22", "2020-07-23"),
        ("000852.SH", "3s", "2025-12-31", "2026-01-01"),
        ("000852.SH", "15s", "2024-01-02", "2024-01-03"),
        ("000852.SH", "1m", "2024-02-30", "2024-03-01"),
    ],
)
def test_request_denied(symbol, freq, start, end):
    with pytest.raises(ValueError):
        validate_request(symbol, freq, start, end)


def test_source_clock_same_second_and_tamper(tmp_path):
    p = tmp_path / "data"
    p.mkdir()
    f = p / "x.parquet"
    pd.DataFrame(
        {
            "symbol": ["000688.SH"] * 2,
            "trading_day": ["2024-01-02"] * 2,
            "observation_datetime": ["2024-01-02T09:30:00Z"] * 2,
            "row_index": [1, 2],
            "price": [1000.0, 1001.0],
        }
    ).to_parquet(f, index=False)
    item = {
        "path": "data/x.parquet",
        "symbol": "000688.SH",
        "frequency": "3s",
        "first_day": "2024-01-02",
        "last_day": "2024-01-02",
        "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
    }
    (p / "manifest.json").write_text(json.dumps({"files": [item]}))
    frame = load_market_data("000688.SH", "3s", "2024-01-02", "2024-01-02", root=tmp_path)
    assert len(frame) == 2 and frame.market_time_shanghai.dt.hour.tolist() == [9, 9]
    with f.open("ab") as out:
        out.write(b"tamper")
    with pytest.raises(ValueError, match="hash"):
        load_market_data("000688.SH", "3s", "2024-01-02", "2024-01-02", root=tmp_path)


@pytest.mark.parametrize(
    "name,body", [("paper.pdf", b"%PDF-1.7"), ("paper.PDF", b"x"), ("papers.zip", b"PK"), ("fake.bin", b"%PDF-1.7"), (".env", b"secret")]
)
def test_nonpublic_payload_rejected(tmp_path, name, body):
    (tmp_path / name).write_bytes(body)
    with pytest.raises(ValueError):
        public_files(tmp_path)


def test_project_clock_guards():
    assert resolve_execution_window(default_data_contract("1m")) == "next_tradable_after_bar_close"
    with pytest.raises(ValueError):
        resolve_execution_window(default_data_contract("1d"), execution_window="next_session")
    with pytest.raises(ValueError):
        assert_no_local_bar_resample("2m")


def test_project_normalization_and_multiplicity():
    assert empirical_location(2, np.array([1, 2, 3])) == pytest.approx(2 / 3)
    r = evaluate_benjamini_hochberg([0.01, 0.5, 0.03])
    assert r["adjusted_p_values"] == pytest.approx([0.03, 0.5, 0.045])
