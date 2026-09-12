# Excerpt of /home/starryocean/桌面/量化/unified_datahub/scripts/import_local_minute_archives.py
# Baidu zip to lake 1m

# ---- import_local_minute_archives.py:335-368 ----
def build_baidu_netdisk_daily_archive_specs(
    *,
    plan_path: Path,
    download_root: Path,
    frequency: str,
    market: str = "cn_a",
    symbol_filter: frozenset[str] | None = None,
) -> list[ArchiveSpec]:
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    specs: list[ArchiveSpec] = []
    for item in plan.get("files", []):
        remote_path = str(item.get("remote_path") or "")
        if not remote_path:
            continue
        matched_freqs = set(item.get("matched_frequencies") or [])
        if matched_freqs and frequency not in matched_freqs:
            continue
        if not _remote_path_matches_frequency(remote_path, frequency):
            continue
        local_path = download_root / remote_path.lstrip("/")
        if not local_path.exists():
            import logging as _logging
            _logging.getLogger(__name__).warning("skipping missing downloaded Baidu Netdisk archive: %s", local_path)
            continue
        group = str(item.get("instrument_group") or _infer_baidu_instrument_group(remote_path))
        specs.append(
            ArchiveSpec(
                path=local_path,
                source_kind=f"baidu_netdisk_{group}_archive",
                instrument_group=group,
                market=market,
                symbols=symbol_filter,
            )
        )

# ---- import_local_minute_archives.py:964-1050 ----
def _bars_table_from_source(
    source: pa.Table,
    *,
    symbol: str,
    source_kind: str,
    instrument_type: str | None = None,
    market: str = "cn_a",
    dataset_version: str,
    ingested_at: str,
) -> pa.Table:
    n = source.num_rows
    timestamp = _timestamp_column(_required_column(source, "时间", "timestamp", "datetime", "date"))
    ts_text = pc.binary_join_element_wise(
        pc.strftime(timestamp, format="%Y-%m-%dT%H:%M:%S"),
        pa.scalar("Z"),
        "",
    )
    instrument_type = instrument_type or _instrument_type_from_source_kind(source_kind)
    trading_day = _trading_day_column(timestamp, market=market, instrument_type=instrument_type)
    trading_month = pc.utf8_slice_codeunits(trading_day, start=0, stop=7)
    result = pa.table(
        {
            "symbol": pa.array([symbol] * n, type=pa.string()),
            "market": pa.array([market] * n, type=pa.string()),
            "instrument_type": pa.array([instrument_type] * n, type=pa.string()),
            "timestamp": ts_text,
            "trading_day": trading_day,
            "trading_month": trading_month,
            "open": _numeric_column(source, "开盘价", "open"),
            "high": _numeric_column(source, "最高价", "high"),
            "low": _numeric_column(source, "最低价", "low"),
            "close": _numeric_column(source, "收盘价", "close"),
            "volume": _numeric_column(source, "成交量", "volume", "vol"),
            "amount": _numeric_column(source, "成交额", "amount", "money", "turnover", default=0.0),
            "available_at": pa.array([ingested_at] * n, type=pa.string()),
            "ingested_at": pa.array([ingested_at] * n, type=pa.string()),
            "source_kind": pa.array([source_kind] * n, type=pa.string()),
            "dataset_version": pa.array([dataset_version] * n, type=pa.string()),
        },
        schema=BAR_SCHEMA,
    )
    return result


def _required_column(source: pa.Table, *names: str) -> pa.ChunkedArray:
    for name in names:
        if name in source.column_names:
            return source[name]
    raise KeyError(f"missing required column; expected one of {names}")


def _numeric_column(source: pa.Table, *names: str, default: float | None = None) -> pa.ChunkedArray:
    for name in names:
        if name in source.column_names:
            return pc.cast(source[name], pa.float64(), safe=False)
    if default is None:
        raise KeyError(f"missing required numeric column; expected one of {names}")
    return pa.chunked_array([pa.array([default] * source.num_rows, type=pa.float64())])


def _trading_day_column(
    timestamp: pa.ChunkedArray,
    *,
    market: str,
    instrument_type: str,
) -> pa.ChunkedArray:
    if market == FUTURES_MARKET and instrument_type == "futures":
        night_mask = pc.greater_equal(
            pc.strftime(timestamp, format="%H:%M:%S"),
            pa.scalar("21:00:00"),
        )
        shifted = pc.add(timestamp, pa.scalar(86400, type=pa.duration("s")))
        return pc.strftime(pc.if_else(night_mask, shifted, timestamp), format="%Y-%m-%d")
    return pc.strftime(timestamp, format="%Y-%m-%d")


def _timestamp_column(raw: pa.ChunkedArray) -> pa.ChunkedArray:
    raw_type = raw.type
    if pa.types.is_timestamp(raw_type):
        return raw
    if not (pa.types.is_string(raw_type) or pa.types.is_large_string(raw_type)):
        raw = pc.cast(raw, pa.string(), safe=False)
    parsed = pc.coalesce(
        pc.strptime(raw, format="%Y-%m-%d %H:%M:%S", unit="s", error_is_null=True),
        pc.strptime(raw, format="%Y-%m-%d %H:%M", unit="s", error_is_null=True),
        pc.strptime(raw, format="%Y/%m/%d %H:%M:%S", unit="s", error_is_null=True),
        pc.strptime(raw, format="%Y/%m/%d %H:%M", unit="s", error_is_null=True),
