#!/usr/bin/env python3
"""Export the 2025-12-01 source-day extracts. Filter by instrument and
trading_day only. Do not drop rows by minute, spread, volume, or price
validity. Do not convert clocks, fill prices, or invent missing fields.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

LAKE = Path("/home/starryocean/桌面/量化/unified_datahub/.runtime/live/lake")
DAY = "2025-12-01"
QUOTE_VERSION = (
    "fund_cb_l2_quote_change_cn_a_3s_baidu_shidang_20250901_20260828_v1_20260902"
)
TRADE_VERSION = "fund_cb_tick_trades_cn_a_baidu_shidang_20250901_20260828_v1_20260902"
INDEX_VERSION = (
    "market_index_baidu_3s_20000714_20260821_cffex_underlyings_alias_repaired_v4_20260823"
)
QUOTE_SRC = (
    LAKE
    / "fund_cb_l2_quote_change_recent_1y"
    / f"dataset_version={QUOTE_VERSION}"
    / "trading_month=2025-12"
    / f"trading_day={DAY}.parquet"
)
TRADE_SRC = (
    LAKE
    / "fund_cb_tick_trades_recent_1y"
    / f"dataset_version={TRADE_VERSION}"
    / "trading_month=2025-12"
    / f"trading_day={DAY}.parquet"
)
INDEX_SRC = (
    LAKE
    / "market_index_transactions"
    / f"dataset_version={INDEX_VERSION}"
    / "observations.parquet"
)
ETF_CODES = ("512100", "588000")
INDEX_SYMBOLS = ("000852.SH", "000688.SH")
PACK = Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def schema_json(table: pa.Table) -> list[dict[str, str]]:
    return [{"name": field.name, "type": str(field.type)} for field in table.schema]


def write_table(table: pa.Table, dest: Path) -> dict[str, object]:
    dest.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, dest, compression="zstd", use_dictionary=True)
    return {
        "path": str(dest.relative_to(PACK)),
        "rows": table.num_rows,
        "bytes": dest.stat().st_size,
        "sha256": sha256_file(dest),
        "columns": schema_json(table),
    }


def first_last(values: list[object]) -> dict[str, object]:
    clean = [value for value in values if value is not None and str(value) != ""]
    if not clean:
        return {"first": None, "last": None, "n_nonnull": 0}
    return {"first": str(clean[0]), "last": str(clean[-1]), "n_nonnull": len(clean)}


def main() -> None:
    if not QUOTE_SRC.is_file() or not TRADE_SRC.is_file() or not INDEX_SRC.is_file():
        raise SystemExit(
            f"missing source partition: quote={QUOTE_SRC.exists()} "
            f"trade={TRADE_SRC.exists()} index={INDEX_SRC.exists()}"
        )

    conn = duckdb.connect(database=":memory:")
    # hive_partitioning=false: do not inject path dataset_version/trading_month.
    quote_codes = conn.execute(
        "SELECT code, instrument_id, COUNT(*) AS n "
        "FROM read_parquet(?, hive_partitioning=false) "
        "WHERE code IN (?, ?) GROUP BY 1, 2 ORDER BY 1",
        [str(QUOTE_SRC), *ETF_CODES],
    ).fetchall()
    trade_codes = conn.execute(
        "SELECT code, instrument_id, COUNT(*) AS n "
        "FROM read_parquet(?, hive_partitioning=false) "
        "WHERE code IN (?, ?) GROUP BY 1, 2 ORDER BY 1",
        [str(TRADE_SRC), *ETF_CODES],
    ).fetchall()
    index_hits = conn.execute(
        "SELECT symbol, COUNT(*) AS n "
        "FROM read_parquet(?, hive_partitioning=false) "
        "WHERE trading_day = ? AND symbol IN (?, ?) GROUP BY 1 ORDER BY 1",
        [str(INDEX_SRC), DAY, *INDEX_SYMBOLS],
    ).fetchall()

    files: dict[str, dict[str, object]] = {}
    for code in ETF_CODES:
        quote = conn.execute(
            "SELECT * FROM read_parquet(?, hive_partitioning=false) "
            "WHERE code = ? ORDER BY event_seq, market_observed_at",
            [str(QUOTE_SRC), code],
        ).fetch_arrow_table()
        trade = conn.execute(
            "SELECT * FROM read_parquet(?, hive_partitioning=false) "
            "WHERE code = ? ORDER BY trade_seq, market_observed_at",
            [str(TRADE_SRC), code],
        ).fetch_arrow_table()
        files[f"quotes/{code}_20251201.parquet"] = write_table(
            quote, PACK / "quotes" / f"{code}_20251201.parquet"
        )
        files[f"trades/{code}_20251201.parquet"] = write_table(
            trade, PACK / "trades" / f"{code}_20251201.parquet"
        )

    for symbol in INDEX_SYMBOLS:
        code = symbol.split(".", 1)[0]
        index = conn.execute(
            "SELECT * FROM read_parquet(?, hive_partitioning=false) "
            "WHERE trading_day = ? AND symbol = ? "
            "ORDER BY observation_datetime, row_index",
            [str(INDEX_SRC), DAY, symbol],
        ).fetch_arrow_table()
        files[f"index_3s/{code}_20251201.parquet"] = write_table(
            index, PACK / "index_3s" / f"{code}_20251201.parquet"
        )

    observations: dict[str, object] = {}
    for key, meta in files.items():
        path = PACK / key
        table = pq.read_table(path)
        colset = set(table.column_names)
        rec: dict[str, object] = {"rows": table.num_rows, "columns": table.column_names}
        for name in (
            "time_raw",
            "market_observed_at",
            "valid_from",
            "valid_until",
            "ingested_at",
            "observation_datetime",
            "observation_time",
            "source_file_sha256",
            "source_archive_sha256",
            "source_kind",
            "update_type",
            "is_checkpoint",
            "session_phase",
            "iopv_raw",
            "timestamp_mode",
            "trade_code",
        ):
            if name not in colset:
                continue
            values = table[name].to_pylist()
            if name in {
                "update_type",
                "session_phase",
                "iopv_raw",
                "timestamp_mode",
                "trade_code",
                "source_kind",
            }:
                counts: dict[str, int] = {}
                for value in values:
                    counts[str(value)] = counts.get(str(value), 0) + 1
                rec[name] = {"distinct": counts}
            elif name == "is_checkpoint":
                rec[name] = {
                    "true": sum(1 for value in values if value is True),
                    "false": sum(1 for value in values if value is False),
                }
            elif name in {"source_file_sha256", "source_archive_sha256"}:
                rec[name] = sorted({str(value) for value in values if value})
            else:
                rec[name] = first_last(values)
        if "time_raw" in colset:
            vicinity = [
                value
                for value in table["time_raw"].to_pylist()
                if str(value).zfill(9)[:4] == "1326"
            ]
            rec["time_raw_1326_hhmm_count"] = len(vicinity)
            rec["time_raw_1326_hhmm_first_last"] = first_last(vicinity)
        observations[key] = rec

    export_receipt = {
        "schema_id": "factorlab_etf_one_day_source_export@1.0",
        "trading_day": DAY,
        "filter": {
            "etf": "code IN ('512100','588000'); no minute/spread/volume/price filter",
            "index": "trading_day='2025-12-01' AND symbol IN ('000852.SH','000688.SH'); no other filter",
        },
        "transforms": [
            "SELECT *",
            "stable ORDER BY native sequence columns",
            "write parquet zstd",
        ],
        "not_done": [
            "clock shift",
            "dedupe",
            "price fill",
            "quantity=0 rewrite",
            "ingested_at renamed as exchange publish time",
            "x10000 conversion",
            "snapshot reconstruction into a second file",
        ],
        "source_identity_probe": {
            "quote_code_instrument_id": [list(row) for row in quote_codes],
            "trade_code_instrument_id": [list(row) for row in trade_codes],
            "index_symbol_counts": [list(row) for row in index_hits],
        },
        "files": files,
        "field_observations": observations,
        "exported_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (PACK / "export_receipt.json").write_text(
        json.dumps(export_receipt, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: files[key]["rows"] for key in files}, indent=2))


if __name__ == "__main__":
    main()
