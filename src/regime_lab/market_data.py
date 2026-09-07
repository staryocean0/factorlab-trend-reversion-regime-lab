"""Verified, bounded reader for the unchanged two-index input package."""

import hashlib
import json
from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]


def validate_request(symbol, frequency, start, end):
    if symbol not in {"000688.SH", "000852.SH"} or frequency not in {"3s", "1m", "5m"}:
        raise ValueError("instrument/frequency outside the supplied package")
    begin, finish = date.fromisoformat(start), date.fromisoformat(end)
    earliest = "2020-07-23" if symbol == "000688.SH" else ("2014-10-17" if frequency == "3s" else "2015-01-05")
    if start != begin.isoformat() or end != finish.isoformat() or start < earliest or end > "2025-12-31" or begin > finish:
        raise ValueError("date interval outside the declared data role")


def load_market_data(symbol, frequency, start, end, *, root=ROOT):
    validate_request(symbol, frequency, start, end)
    root = Path(root).resolve()
    manifest = json.loads((root / "data/manifest.json").read_text())
    parts = []
    for item in manifest["files"]:
        if (item["symbol"], item["frequency"]) != (symbol, frequency) or item["last_day"] < start or item["first_day"] > end:
            continue
        path = (root / item["path"]).resolve()
        if not path.is_relative_to(root):
            raise ValueError("manifest path escapes repository")
        with path.open("rb") as handle:
            actual = hashlib.file_digest(handle, "sha256").hexdigest()
        if actual != item["sha256"]:
            raise ValueError("input hash mismatch")
        frame = pq.read_table(path, filters=[("trading_day", ">=", start), ("trading_day", "<=", end)]).to_pandas()
        if set(frame.symbol) - {symbol}:
            raise ValueError("unexpected symbol")
        parts.append(frame)
    if not parts:
        return pd.DataFrame()
    frame = pd.concat(parts, ignore_index=True)
    clock = "observation_datetime" if frequency == "3s" else "timestamp"
    frame["market_time_shanghai"] = pd.to_datetime(frame[clock].str[:19]).dt.tz_localize("Asia/Shanghai")
    if not (frame.market_time_shanghai.dt.strftime("%Y-%m-%d") == frame.trading_day).all():
        raise ValueError("calendar and clock disagree")
    keys = ["market_time_shanghai", "row_index"] if frequency == "3s" else ["market_time_shanghai"]
    return frame.sort_values(keys, kind="stable").reset_index(drop=True)
