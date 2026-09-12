# Excerpt of /home/starryocean/桌面/量化/baylum terminal 0.4.1/factor_lab/src/factor_lab/data/unified_kline_v2.py
# FactorLab parallel densify

# ---- unified_kline_v2.py:76-120 ----
def _densify_official_one_minute_path(path: pd.DataFrame) -> pd.DataFrame:
    expected_minutes = (*range(571, 691), *range(781, 901))
    parts: list[pd.DataFrame] = []
    prior_close: float | None = None
    for trading_day, part in path.groupby("trading_day", sort=True):
        work = part.copy()
        minute = work["timestamp"].dt.hour * 60 + work["timestamp"].dt.minute
        work = work.loc[minute.isin(expected_minutes)].copy()
        by_minute = {
            int(row.timestamp.hour * 60 + row.timestamp.minute): row
            for row in work.itertuples(index=False)
        }
        if str(trading_day) in KNOWN_SHORT_TRADING_DAYS:
            if not work.empty:
                prior_close = float(work.iloc[-1]["close"])
                parts.append(work)
            continue
        rows: list[dict[str, Any]] = []
        for minute_of_day in expected_minutes:
            observed = by_minute.get(minute_of_day)
            if observed is not None:
                payload = observed._asdict()
                payload["causal_flat_fill"] = False
                prior_close = float(payload["close"])
            else:
                if prior_close is None:
                    raise ValueError(
                        f"cannot causally fill leading Cloudridge 1m gap: "
                        f"{trading_day} {minute_of_day}"
                    )
                timestamp = pd.Timestamp(trading_day) + pd.Timedelta(minutes=minute_of_day)
                payload = {
                    "timestamp": timestamp,
                    "trading_day": str(trading_day),
                    "open": prior_close,
                    "high": prior_close,
                    "low": prior_close,
                    "close": prior_close,
                    "causal_flat_fill": True,
                }
            rows.append(payload)
        parts.append(pd.DataFrame(rows))
    if not parts:
        raise ValueError("Cloudridge 1m path has no official-session rows")
    return pd.concat(parts, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
