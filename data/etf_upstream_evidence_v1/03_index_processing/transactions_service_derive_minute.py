# Excerpt of /home/starryocean/桌面/量化/unified_datahub/src/datahub/core/services/market_indices/transactions_service.py
# 3s to 1m available_at 15:30+08:00

# ---- transactions_service.py:696-763 ----
def _derive_minute_rows(
    *, parquet_path: Path, dataset_version: str
) -> list[dict[str, Any]]:
    with duckdb.connect(database=":memory:") as conn:
        source = (
            conn.execute(
                "SELECT * FROM read_parquet(?) ORDER BY symbol, observation_datetime, row_index",
                [str(parquet_path)],
            )
            .fetchdf()
            .to_dict("records")
        )
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in source:
        label = _minute_label(str(row["observation_time"]))
        if label is None:
            continue
        grouped[(str(row["symbol"]), str(row["trading_day"]), label)].append(row)
    output: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()
    for (symbol, day, label), rows in sorted(grouped.items()):
        rows.sort(
            key=lambda item: (str(item["observation_datetime"]), int(item["row_index"]))
        )
        prices = [float(item["price"]) for item in rows]
        output.append(
            {
                "symbol": symbol,
                "market": MARKET,
                "instrument_type": "market_index",
                "timestamp": f"{day}T{label}:00Z",
                "trading_day": day,
                "trading_month": day[:7],
                "open": prices[0],
                "high": max(prices),
                "low": min(prices),
                "close": prices[-1],
                "volume": None,
                "amount": sum(float(item["amount"]) for item in rows),
                "available_at": f"{day}T15:30:00+08:00",
                "ingested_at": now,
                "source_kind": "market_index_transaction_derived_1m",
                "dataset_version": dataset_version,
            }
        )
    return output


def _minute_label(value: str) -> str | None:
    hour, minute, second = (int(item) for item in value[:8].split(":"))
    total = hour * 60 + minute
    if 9 * 60 + 25 <= total < 9 * 60 + 30:
        return "09:31"
    if 9 * 60 + 30 <= total < 11 * 60 + 29:
        return _format_minute(total + 1)
    if 11 * 60 + 29 <= total <= 11 * 60 + 30:
        return "11:30"
    if 13 * 60 <= total < 14 * 60 + 58:
        return _format_minute(total + 1)
    if 14 * 60 + 58 <= total < 15 * 60:
        return _format_minute(min(total + 1, 15 * 60))
    if total == 15 * 60 and second <= 59:
        return "15:00"
    return None


def _format_minute(value: int) -> str:
    return f"{value // 60:02d}:{value % 60:02d}"
