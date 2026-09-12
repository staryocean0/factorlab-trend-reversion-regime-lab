# Excerpt of /home/starryocean/桌面/量化/factorlab-trend-reversion-regime-lab/research/r1a_carrier_transport/export_datahub_lake.py
# lake to uploaded CSV

# ---- export_datahub_lake.py:16-21 ----
DATASET_VERSION = "bars_cn_a_1m_raw_canonical_4ceca170a851"
LAKE_REL = (
    ".runtime/live/lake/bars/"
    f"dataset_version={DATASET_VERSION}/instrument_type=etf"
)
WINDOW = {"start": "2021-01-01", "end": "2025-12-31"}

# ---- export_datahub_lake.py:76-89 ----
def _parse_datahub_wall_clock(values: pd.Series) -> pd.Series:
    text = values.astype(str)
    if bool(text.str.endswith("Z").all()):
        parsed = pd.to_datetime(text.str.removesuffix("Z"), errors="raise")
        return parsed.dt.tz_localize("Asia/Shanghai")
    parsed = pd.to_datetime(text, errors="raise")
    if parsed.dt.tz is None:
        return parsed.dt.tz_localize("Asia/Shanghai")
    return parsed.dt.tz_convert("Asia/Shanghai")


def _session_mask(index: pd.DatetimeIndex) -> pd.Series:
    clock = index.hour * 60 + index.minute
    return ((clock >= 570) & (clock <= 690)) | ((clock >= 781) & (clock <= 900))

# ---- export_datahub_lake.py:107-128 ----
def _to_canonical(frame: pd.DataFrame, carrier: str) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    if missing := sorted(required.difference(frame.columns)):
        raise ValueError(f"missing lake columns: {missing}")
    out = frame.copy()
    out["timestamp"] = _parse_datahub_wall_clock(out["timestamp"])
    out = out.loc[_session_mask(pd.DatetimeIndex(out["timestamp"]))].copy()
    days = out["timestamp"].dt.strftime("%Y-%m-%d")
    out = out.loc[(days >= WINDOW["start"]) & (days <= WINDOW["end"])].copy()
    for col in ("open", "high", "low", "close", "volume"):
        out[col] = pd.to_numeric(out[col], errors="raise")
    out["symbol"] = carrier
    out["timestamp"] = out["timestamp"].map(lambda ts: ts.isoformat())
    out = out[["symbol", "timestamp", "open", "high", "low", "close", "volume"]]
    out = out.sort_values("timestamp", kind="mergesort").drop_duplicates("timestamp", keep="last")
    if out.empty:
        raise ValueError(f"empty canonical export for {carrier}")
    if not out[["open", "high", "low", "close"]].gt(0).all().all():
        raise ValueError(f"nonpositive OHLC for {carrier}")
    if (out["volume"] < 0).any():
        raise ValueError(f"negative volume for {carrier}")
    return out.reset_index(drop=True)

# ---- export_datahub_lake.py:166-184 ----
    manifest = {
        "symbol": carrier,
        "source": spec["source"],
        "source_reference": spec["source_reference"],
        "frequency": "1m",
        "timezone": "Asia/Shanghai",
        "bar_label": "bar_end",
        "price_basis": "unadjusted_actual_traded_OHLC",
        "volume_unit": "shares",
        "zero_volume_semantics": "not_an_observed_trade",
        "research_use_authorized": True,
        "corporate_actions_complete": True,
        "corporate_actions_reference": spec["corporate_actions_reference"],
        "corporate_actions_window": WINDOW,
        "files": files,
        "corporate_actions_file": actions_file,
        "dataset_version": DATASET_VERSION,
        "volume_note": "DataHub raw canonical 1m volume is exchange-reported share quantity",
    }
