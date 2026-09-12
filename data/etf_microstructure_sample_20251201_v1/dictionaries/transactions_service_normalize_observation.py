# Excerpt of /home/starryocean/桌面/量化/unified_datahub/src/datahub/core/services/market_indices/transactions_service.py
# Baidu 3s required columns, Z suffix on naive parse, volume=None

# ---- transactions_service.py:32-38 ----
DATASET_KIND = "market_index_transactions"
DATASET_ID = "market_index_transactions_cn_3s"
SCHEMA_VERSION = "market_index_transactions.v1"
FREQUENCY = "3s"
MARKET = "cn_index"
BAIDU_SOURCE_KIND = "baidu_netdisk_market_index_transaction_3s"
TDX_SOURCE_KIND = "tdx_market_index_history_transaction_reconstructed_3s"

# ---- transactions_service.py:80-81 ----
class MarketIndexTransactionArchiveReader:
    REQUIRED_COLUMNS = ("时间", "价位", "成交额")

# ---- transactions_service.py:139-164 ----
        with zipfile.ZipFile(zip_path) as archive:
            for name in sorted(archive.namelist()):
                definition = by_member.get(Path(name).name)
                if definition is None:
                    continue
                seen_members.add(Path(name).name)
                reader = csv.DictReader(
                    io.StringIO(archive.read(name).decode("utf-8-sig"))
                )
                if tuple(reader.fieldnames or []) != self.REQUIRED_COLUMNS:
                    raise ValueError(
                        f"unsupported market-index transaction header in {name}: {reader.fieldnames}"
                    )
                for row_index, raw in enumerate(reader):
                    try:
                        normalized = _normalize_observation(
                            definition=definition,
                            observation_datetime=str(raw.get("时间") or ""),
                            price=raw.get("价位"),
                            amount=raw.get("成交额"),
                            source_kind=BAIDU_SOURCE_KIND,
                            timestamp_mode="source_exact_3s",
                            source_file=name,
                            source_archive_sha256=archive_sha,
                            row_index=row_index,
                        )

# ---- transactions_service.py:614-649 ----
def _normalize_observation(
    *,
    definition: MarketIndexDefinition,
    observation_datetime: str,
    price: object,
    amount: object,
    source_kind: str,
    timestamp_mode: str,
    source_file: str,
    source_archive_sha256: str,
    row_index: int,
) -> dict[str, Any]:
    value = datetime.strptime(observation_datetime, "%Y-%m-%d %H:%M:%S")
    price_value = float(str(price))
    amount_value = float(str(amount))
    if price_value <= 0 or amount_value < 0:
        raise ValueError(f"invalid market-index observation: {observation_datetime}")
    return {
        "symbol": definition.symbol,
        "index_code": definition.index_code,
        "market": MARKET,
        "instrument_type": "market_index",
        "exchange": definition.exchange,
        "observation_datetime": value.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trading_day": value.date().isoformat(),
        "observation_time": value.strftime("%H:%M:%S"),
        "price": price_value,
        "amount": amount_value,
        "volume": None,
        "session_phase": _session_phase(value.strftime("%H:%M:%S")),
        "timestamp_mode": timestamp_mode,
        "source_kind": source_kind,
        "source_file": source_file,
        "source_archive_sha256": source_archive_sha256,
        "row_index": int(row_index),
    }

# ---- transactions_service.py:766-775 ----
def _session_phase(value: str) -> str:
    if "09:15:00" <= value <= "09:24:59":
        return "pre_open_auction"
    if "09:25:00" <= value <= "09:29:59":
        return "open_call_auction"
    if ("09:30:00" <= value <= "11:30:59") or ("13:00:00" <= value <= "14:56:59"):
        return "continuous_auction"
    if "14:57:00" <= value <= "15:00:59":
        return "close_auction"
    return "outside_session"
