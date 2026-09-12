# Excerpt of /home/starryocean/桌面/量化/unified_datahub/scripts/materialize_fund_cb_l2_recent_1y.py
# HQ/CJ column map, HHMMSSmmm->ns, checkpoint/delta eventize, tick normalize

# ---- materialize_fund_cb_l2_recent_1y.py:80-116 ----
HQ_COLS = {  # source column -> normalized name (行情.csv / ten-level 3s snapshot)
    "交易所代码": "code",
    "时间": "time_raw",
    "成交价": "last_price_x10000",
    "成交量": "volume",
    "成交额": "amount",
    "成交笔数": "trade_count",
    "IOPV": "iopv_raw",
    "当日累计成交量": "cum_volume",
    "当日成交额": "cum_amount",
    "最高价": "high_x10000",
    "最低价": "low_x10000",
    "开盘价": "open_x10000",
    "前收盘": "prev_close_x10000",
    "叫卖总量": "ask_size_total",
    "叫买总量": "bid_size_total",
    "成交标志": "trade_flag_raw",
    "BS标志": "bs_flag_raw",
}
for _i in range(1, 11):
    HQ_COLS[f"申卖价{_i}"] = f"ask_price_x10000_{_i}"
    HQ_COLS[f"申卖量{_i}"] = f"ask_size_{_i}"
    HQ_COLS[f"申买价{_i}"] = f"bid_price_x10000_{_i}"
    HQ_COLS[f"申买量{_i}"] = f"bid_size_{_i}"

CJ_COLS = {  # 逐笔成交.csv
    "交易所代码": "code",
    "时间": "time_raw",
    "成交编号": "trade_seq_raw",
    "成交代码": "trade_code",
    "委托代码": "order_kind",
    "BS标志": "bs_flag",
    "成交价格": "price_x10000",
    "成交数量": "volume",
    "叫卖序号": "ask_order_id",
    "叫买序号": "bid_order_id",
}

# ---- materialize_fund_cb_l2_recent_1y.py:247-258 ----
def _time_raw_to_ns(day: str, time_raw: pd.Series) -> pd.Series:
    """Vectorized HHMMSSmmm -> ns since epoch (Asia/Shanghai naive)."""
    t = pd.to_numeric(time_raw, errors="coerce").fillna(0).astype("int64")
    hh = t // 10_000_000
    mm = (t // 100_000) % 100
    ss = (t // 1_000) % 100
    ms = t % 1_000
    base = pd.Timestamp(
        int(day[0:4]), int(day[4:6]), int(day[6:8])
    ).value  # ns
    ns = base + hh * 3_600_000_000_000 + mm * 60_000_000_000 + ss * 1_000_000_000 + ms * 1_000_000
    return pd.Series(ns, index=time_raw.index, dtype="int64")

# ---- materialize_fund_cb_l2_recent_1y.py:381-488 ----
        hq["market_observed_at"] = _time_raw_to_ns(day, hq["time_raw"].astype(str))
        for col in INT64_HQ:
            if col in hq.columns:
                hq[col] = _to_int64(hq[col])
        overflow_cells = 0
        for col in FLOAT_HQ:
            if col in hq.columns:
                hq[col], _n = _to_float_guarded(hq[col])
                overflow_cells += _n
        result["overflow_cells"] = overflow_cells
        for col in ["iopv_raw", "trade_flag_raw", "bs_flag_raw"]:
            if col in hq.columns:
                hq[col] = hq[col].astype(str).str.strip()
        hq = hq.sort_values("market_observed_at", kind="stable").reset_index(drop=True)
        hq["session_phase"] = _session_phase(hq["market_observed_at"])

        state = hq[STATE_COLS].astype("float64").to_numpy()
        phase = hq["session_phase"].to_numpy()
        seg_break = np.concatenate(([True], phase[1:] != phase[:-1]))
        changed = np.ones(len(hq), dtype=bool)
        if len(hq) > 1:
            diff = np.zeros(len(hq), dtype=bool)
            prev = state[:-1]
            curr = state[1:]
            both_nan = np.isnan(prev) & np.isnan(curr)
            neq = (prev != curr) & ~both_nan
            diff[1:] = neq.any(axis=1)
            changed = diff | seg_break
        event_idx = np.nonzero(changed)[0]
        events = hq.iloc[event_idx].copy()
        events["is_checkpoint"] = seg_break[event_idx]
        events["update_type"] = np.where(seg_break[event_idx], "checkpoint", "delta")
        events["event_seq"] = np.arange(len(events), dtype="int64")
        day_close = pd.Timestamp(int(day[0:4]), int(day[4:6]), int(day[6:8]), 15).value
        ts_vals = events["market_observed_at"].to_numpy(dtype="int64")
        events["valid_from"] = events["market_observed_at"]
        events["valid_until"] = np.append(ts_vals[1:], day_close)
        seg_ids = np.cumsum(seg_break) - 1
        ev_seg = seg_ids[event_idx]
        events["is_session_last"] = np.append(ev_seg[1:] != ev_seg[:-1], True)

        # replay audit: rebuilt state at every source row position == source row
        rebuilt = np.empty_like(state)
        starts = event_idx
        ends = np.append(event_idx[1:], len(hq))
        for s, e, pos in zip(starts, ends, event_idx):
            rebuilt[s:e] = state[pos]
        both_nan = np.isnan(rebuilt) & np.isnan(state)
        mismatch = ((rebuilt != state) & ~both_nan).any(axis=1)
        result["replay_mismatch"] = int(mismatch.sum())
        result["replay_checked"] = int(len(hq))
        ask10 = hq["ask_price_x10000_10"].notna() & (hq["ask_price_x10000_10"] > 0)
        bid10 = hq["bid_price_x10000_10"].notna() & (hq["bid_price_x10000_10"] > 0)
        result["ten_level_populated"] = int((ask10 & bid10).sum())
        a1 = hq["ask_price_x10000_1"].astype("float64")
        b1 = hq["bid_price_x10000_1"].astype("float64")
        result["locked_or_crossed"] = int(((a1.notna()) & (b1.notna()) & (a1 > 0) & (b1 > 0) & (a1 < b1)).sum())
        result["quote_rows"] = int(len(hq))
        result["first_ts"] = int(hq["market_observed_at"].iloc[0])
        result["last_ts"] = int(hq["market_observed_at"].iloc[-1])
        events["instrument_id"] = f"{code}.{exchange}"
        events["instrument_type"] = itype
        events["exchange"] = exchange
        events["identity_source"] = id_source
        events["trading_day"] = _day_to_iso(day)
        events["source_kind"] = SOURCE_KIND
        events["source_day"] = day
        events["source_file_sha256"] = archive_sha
        events["ingested_at"] = ingested_at
        events["time_authority"] = TIME_AUTHORITY
        events["receipt_exact_pit"] = False
        for _c in ("market_observed_at", "valid_from", "valid_until"):
            events[_c] = pd.to_datetime(events[_c], unit="ns")
        qfrag = Path(frag_root) / "quote" / f"{code}.parquet"
        _write_fragment(events, qfrag)
        result["quote_frag"] = str(qfrag)
        result["event_rows"] = int(len(events))
        del events, hq

    cj = _read_source_csv(sym_path / "逐笔成交.csv", CJ_COLS)
    if cj is not None and len(cj):
        cj = cj[cj["code"].astype(str).str.strip() == code].copy()
    if cj is not None and len(cj):
        cj["market_observed_at"] = _time_raw_to_ns(day, cj["time_raw"].astype(str))
        cj["price_x10000"] = _to_int64(cj["price_x10000"])
        cj["volume"], _tv_bad = _to_float_guarded(cj["volume"])
        result["overflow_cells"] = result.get("overflow_cells", 0) + _tv_bad
        for col in ["trade_seq_raw", "trade_code", "order_kind", "bs_flag", "ask_order_id", "bid_order_id"]:
            cj[col] = cj[col].astype(str).str.strip()
        cj = cj.sort_values("market_observed_at", kind="stable").reset_index(drop=True)
        cj["trade_seq"] = np.arange(len(cj), dtype="int64")
        cj["instrument_id"] = f"{code}.{exchange}"
        cj["instrument_type"] = itype
        cj["exchange"] = exchange
        cj["identity_source"] = id_source
        cj["trading_day"] = _day_to_iso(day)
        cj["source_kind"] = SOURCE_KIND
        cj["source_day"] = day
        cj["source_file_sha256"] = archive_sha
        cj["ingested_at"] = ingested_at
        cj["time_authority"] = TIME_AUTHORITY
        cj["receipt_exact_pit"] = False
        cj["market_observed_at"] = pd.to_datetime(cj["market_observed_at"], unit="ns")
        tfrag = Path(frag_root) / "trades" / f"{code}.parquet"
        _write_fragment(cj, tfrag)
        result["trade_frag"] = str(tfrag)
        result["trade_rows"] = int(len(cj))
        del cj
