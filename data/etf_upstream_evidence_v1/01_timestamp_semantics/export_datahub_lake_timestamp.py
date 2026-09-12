# Excerpt of /home/starryocean/桌面/量化/factorlab-trend-reversion-regime-lab/research/r1a_carrier_transport/export_datahub_lake.py
# Z stripped then Asia/Shanghai; amount dropped

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

# ---- export_datahub_lake.py:107-120 ----
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
