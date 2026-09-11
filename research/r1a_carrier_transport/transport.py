"""Frozen R1_A ETF transport. Missing/unadmitted data never become alpha failure.

Run with PYTHONPATH=src:. python research/r1a_carrier_transport/transport.py
Canonical input manifests: data/r1a_carrier_prices/<ETF>.json (see README).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

HORIZONS = (1, 5, 15, 30, 60, 120, 240)
CARRIERS = {"000852.SH": "512100.SH", "000688.SH": "588000.SH"}
COUNTS = {"000852.SH": 1296, "000688.SH": 1802}
YEARS = tuple(str(y) for y in range(2021, 2026))
WINDOW = {"start": "2021-01-01", "end": "2025-12-31"}
FREEZE_PATH = "docs/governance/R1A_CARRIER_PRICE_TRANSPORT_FREEZE@1.0.json"
PAIRS_PATH = "docs/ops/evidence/r1_incremental_alpha_20260911/matched_pairs.csv"
PAIRS_BLOB = "95191091d1a26c360c3efb5ae2d5be9cf194211d"
INDEX_BLOB = "a1935d30326dc9306dc23cdb309ac463114e2a2a"

class AdmissionError(ValueError):
    """An input contract is missing, incomplete, or inconsistent."""

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def assert_blob(path: Path, expected: str) -> None:
    raw = path.read_bytes()
    got = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if got != expected:
        raise AdmissionError(f"frozen input changed: {path.name}")

def dump(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def shanghai_times(values: pd.Series) -> pd.DatetimeIndex:
    try:
        x = pd.DatetimeIndex(pd.to_datetime(values, format="mixed", errors="raise"))
        return x.tz_localize("Asia/Shanghai") if x.tz is None else x.tz_convert("Asia/Shanghai")
    except (TypeError, ValueError) as exc:
        raise AdmissionError("invalid/mixed timezone timestamps") from exc

def checked_csv(root: Path, spec: dict) -> tuple[pd.DataFrame, dict]:
    path = (root / spec["path"]).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise AdmissionError("missing file or path escapes data root")
    if path.stat().st_size != spec["bytes"] or digest(path) != spec["sha256"]:
        raise AdmissionError("carrier file byte count/hash mismatch")
    frame = pd.read_csv(path, dtype={"symbol": str, "ex_date": str})
    if len(frame) != spec["rows"]:
        raise AdmissionError("carrier file row count mismatch")
    return frame, {"path": spec["path"], "sha256": digest(path), "bytes": path.stat().st_size, "rows": len(frame)}

def validate_prices(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    required = {"symbol", "timestamp", "open", "high", "low", "close", "volume"}
    if frame.empty or required - set(frame):
        raise AdmissionError("empty carrier tape or missing OHLCV columns")
    out = frame.copy()
    if set(out.symbol.astype(str)) != {symbol}:
        raise AdmissionError("wrong carrier symbol")
    out.index = shanghai_times(out.timestamp)
    if out.index.has_duplicates or out.index.hasnans:
        raise AdmissionError("duplicate/missing carrier timestamps")
    if (out.index.second != 0).any() or (out.index.microsecond != 0).any():
        raise AdmissionError("not canonical minute-end timestamps")
    days = out.index.strftime("%Y-%m-%d")
    if (days < WINDOW["start"]).any() or (days > WINDOW["end"]).any():
        raise AdmissionError("carrier rows outside frozen 2021-2025 window")
    clock = out.index.hour * 60 + out.index.minute
    if not (((clock >= 570) & (clock <= 690)) | ((clock >= 781) & (clock <= 900))).all():
        raise AdmissionError("carrier timestamps outside declared exchange sessions")
    for col in ("open", "high", "low", "close", "volume"):
        try:
            out[col] = pd.to_numeric(out[col], errors="raise")
        except (ValueError, TypeError) as exc:
            raise AdmissionError(f"nonnumeric {col}") from exc
    p = out[["open", "high", "low", "close"]].to_numpy(float)
    v = out.volume.to_numpy(float)
    if not np.isfinite(p).all() or (p <= 0).any() or not np.isfinite(v).all() or (v < 0).any():
        raise AdmissionError("invalid/nonfinite OHLCV")
    if ((out.low > out[["open", "close"]].min(axis=1)) | (out.high < out[["open", "close"]].max(axis=1)) | (out.low > out.high)).any():
        raise AdmissionError("invalid OHLC ordering")
    return out.sort_index()

def admit(root: Path, manifest_path: Path, carrier: str, index_times: pd.DatetimeIndex) -> tuple[pd.DataFrame, list[str], dict]:
    if not manifest_path.is_file():
        raise AdmissionError("MISSING_CARRIER_MANIFEST_AND_DELIVERY")
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    exact = {"symbol": carrier, "frequency": "1m", "timezone": "Asia/Shanghai", "bar_label": "bar_end", "price_basis": "unadjusted_actual_traded_OHLC", "volume_unit": "shares", "zero_volume_semantics": "not_an_observed_trade", "research_use_authorized": True, "corporate_actions_complete": True, "corporate_actions_window": WINDOW}
    for key, value in exact.items():
        if m.get(key) != value:
            raise AdmissionError(f"unresolved source metadata: {key}")
    for key in ("source", "source_reference", "corporate_actions_reference"):
        if not isinstance(m.get(key), str) or not m[key].strip() or m[key].upper().startswith("PENDING"):
            raise AdmissionError(f"missing provenance: {key}")
    if not m.get("files") or not m.get("corporate_actions_file"):
        raise AdmissionError("missing carrier delivery or corporate-action ledger")
    frames, file_meta = [], []
    for spec in m["files"]:
        frame, info = checked_csv(root, spec)
        frames.append(frame)
        file_meta.append(info)
    prices = validate_prices(pd.concat(frames, ignore_index=True), carrier)
    actions, action_meta = checked_csv(root, m["corporate_actions_file"])
    if {"symbol", "ex_date", "event_type", "source_reference"} - set(actions):
        raise AdmissionError("corporate-action ledger schema missing")
    if not actions.empty:
        if set(actions.symbol) != {carrier} or actions.ex_date.isna().any() or actions.source_reference.isna().any():
            raise AdmissionError("invalid corporate-action identity/provenance")
        dates = pd.to_datetime(actions.ex_date, format="%Y-%m-%d", errors="raise").dt.strftime("%Y-%m-%d")
        if (dates < WINDOW["start"]).any() or (dates > WINDOW["end"]).any():
            raise AdmissionError("corporate-action ledger outside frozen window")
        ex_dates = sorted(set(dates))
    else:
        ex_dates = []
    observed = prices.index[prices.volume > 0]
    coverage = {}
    for year in YEARS:
        target = index_times[index_times.year == int(year)]
        if len(target) == 0:
            raise AdmissionError("index clock missing evaluation year")
        coverage[year] = float(target.isin(observed).mean())
    if any(x < 0.95 for x in coverage.values()):
        raise AdmissionError("INSUFFICIENT_CARRIER_MINUTE_COVERAGE " + json.dumps(coverage))
    return prices, ex_dates, {"status": "PASS_DATA_ADMISSION_ONLY", "manifest_sha256": digest(manifest_path), "source": m["source"], "source_reference": m["source_reference"], "files": file_meta, "corporate_actions": action_meta, "minute_coverage_by_year": coverage, "zero_volume_rows": int((prices.volume == 0).sum())}

def pair_clock(pairs: pd.DataFrame, times: pd.DatetimeIndex, carrier: str) -> pd.DataFrame:
    rows = []
    for p in pairs.itertuples(index=False):
        for leg in ("event", "control"):
            start = int(getattr(p, leg + "_entry_idx"))
            if start < 0 or start + 240 >= len(times):
                raise AdmissionError("frozen pair outside index clock")
            for h in (0,) + HORIZONS:
                stamp = times[start + h]
                if not WINDOW["start"] <= stamp.strftime("%Y-%m-%d") <= WINDOW["end"]:
                    raise AdmissionError("anchor crossed frozen calendar boundary")
                rows.append({"pair_id": p.pair_id, "index_symbol": p.symbol, "carrier": carrier, "leg": leg, "horizon": h, "index_row": start + h, "timestamp": stamp.isoformat(), "direction": int(p.parent_direction)})
    return pd.DataFrame(rows)

def common_pairs(pairs: pd.DataFrame, times: pd.DatetimeIndex, prices: pd.DataFrame, ex_dates: list[str]) -> tuple[pd.DataFrame, np.ndarray, dict]:
    # Reindex onto the immutable INDEX clock, never move to the next ETF row.
    aligned = prices.reindex(times)
    px = aligned.close.to_numpy(float)
    valid = np.isfinite(px) & (px > 0) & (aligned.volume.to_numpy(float) > 0)
    bad_prefix = np.r_[0, np.cumsum(~valid)]
    days = np.asarray(times.strftime("%Y-%m-%d"))
    ex = np.asarray(ex_dates, dtype=str)
    rows = []
    for p in pairs.itertuples(index=False):
        reasons = []
        for leg in ("event", "control"):
            a = int(getattr(p, leg + "_entry_idx")); b = a + 240
            if a < 0 or b >= len(times):
                raise AdmissionError("pair indices invalid")
            if bad_prefix[b + 1] > bad_prefix[a]:
                reasons.append(leg + "_missing_or_zero_volume_minute")
            if len(ex) and np.any((ex > days[a]) & (ex <= days[b])):
                reasons.append(leg + "_corporate_action_crossing")
        rows.append({"pair_id": p.pair_id, "event_day": p.event_day, "side": p.side, "eligible": not reasons, "reason": ";".join(reasons) or "complete_common_path"})
    audit = pd.DataFrame(rows)
    rates = {"pooled": float(audit.eligible.mean()) if len(audit) else 0.0}
    for year in YEARS:
        y = audit.loc[audit.event_day.astype(str).str.startswith(year)]
        rates[year] = float(y.eligible.mean()) if len(y) else 0.0
    stats = {"frozen_pairs": len(audit), "complete_pairs": int(audit.eligible.sum()), "coverage": rates, "reasons": {str(k): int(v) for k, v in audit.reason.value_counts().items()}, "minimum_coverage_pass": all(v >= 0.80 for v in rates.values())}
    return audit, px, stats

def measure(pairs: pd.DataFrame, index_px: np.ndarray, etf_px: np.ndarray) -> pd.DataFrame:
    rows = []
    for p in pairs.itertuples(index=False):
        e, c, d = int(p.event_entry_idx), int(p.control_entry_idx), int(p.parent_direction)
        if d not in (-1, 1):
            raise AdmissionError("invalid synthetic direction")
        for h in HORIZONS:
            vals = np.array([index_px[e], index_px[e+h], index_px[c], index_px[c+h], etf_px[e], etf_px[e+h], etf_px[c], etf_px[c+h]])
            if not np.isfinite(vals).all() or (vals <= 0).any():
                raise AdmissionError("non-admitted price used in return")
            er, cr = d*(etf_px[e+h]/etf_px[e]-1), d*(etf_px[c+h]/etf_px[c]-1)
            ie, ic = d*(index_px[e+h]/index_px[e]-1), d*(index_px[c+h]/index_px[c]-1)
            path = d*(etf_px[e:e+h+1]/etf_px[e]-1)
            rows.append({"pair_id": p.pair_id, "index_symbol": p.symbol, "event_day": p.event_day, "control_day": p.control_day, "side": p.side, "horizon": h, "etf_event": er, "etf_control": cr, "etf_incremental": er-cr, "index_event_same_sample": ie, "index_control_same_sample": ic, "index_incremental_same_sample": ie-ic, "event_tracking_residual": er-ie, "incremental_tracking_residual": (er-cr)-(ie-ic), "etf_close_MFE": float(path.max()), "etf_close_MAE": float(path.min())})
    return pd.DataFrame(rows)

def describe(frame: pd.DataFrame) -> dict:
    out: dict[str, Any] = {"n": len(frame)}
    for name in ("etf_event", "etf_control", "etf_incremental", "index_event_same_sample", "index_incremental_same_sample", "event_tracking_residual", "incremental_tracking_residual", "etf_close_MFE", "etf_close_MAE"):
        v = frame[name].to_numpy(float) if len(frame) else np.array([])
        out[name] = {"mean_bp": float(v.mean()*1e4) if len(v) else None, "median_bp": float(np.median(v)*1e4) if len(v) else None, "positive_fraction": float((v>0).mean()) if len(v) else None, "std_bp": float(v.std()*1e4) if len(v) else None}
    if len(frame) > 1 and frame.etf_event.std() > 0 and frame.index_event_same_sample.std() > 0:
        out["event_price_return_correlation"] = float(frame.etf_event.corr(frame.index_event_same_sample))
    else:
        out["event_price_return_correlation"] = None
    return out

def summarize(frame: pd.DataFrame) -> dict:
    out = {}
    for h in HORIZONS:
        x = frame.loc[frame.horizon == h]
        out[str(h)] = {"pooled": describe(x), "sides": {s: describe(x.loc[x.side == s]) for s in ("LONG", "SHORT")}, "years": {y: describe(x.loc[x.event_day.astype(str).str.startswith(y)]) for y in YEARS}}
    return out

def run(root: Path, output: Path, manifest_dir: Path) -> dict:
    # Import the original verified reader; no signal engine or matching is run.
    from regime_lab.market_data import load_market_data
    freeze = json.loads((root/FREEZE_PATH).read_text(encoding="utf-8"))
    if freeze["status"] != "FROZEN_BEFORE_CARRIER_OUTCOMES" or freeze["horizons_observed_index_bars"] != list(HORIZONS):
        raise AdmissionError("transport contract drift")
    if freeze["production_authority"] or freeze["blackbox_query_4_authorized"]:
        raise AdmissionError("scope drift")
    if {s: x["carrier"] for s, x in freeze["carriers"].items()} != CARRIERS:
        raise AdmissionError("carrier identity drift")
    assert_blob(root/PAIRS_PATH, PAIRS_BLOB)
    assert_blob(root/"data/manifest.json", INDEX_BLOB)
    pairs = pd.read_csv(root/PAIRS_PATH)
    pairs = pairs.loc[pairs.cell == "R1_A"].copy()
    pairs["pair_id"] = pairs.symbol.astype(str) + ":R1_A:" + pairs.event_entry_idx.astype(str) + ":" + pairs.control_entry_idx.astype(str)
    if pairs.pair_id.duplicated().any():
        raise AdmissionError("duplicate frozen pair")
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        head = None
    receipt = {"schema_id": "factorlab_r1a_carrier_transport_receipt@1.0", "freeze_sha256": digest(root/FREEZE_PATH), "code_commit": head, "matched_pairs_sha256": digest(root/PAIRS_PATH), "input_index_manifest_sha256": digest(root/"data/manifest.json"), "carriers": {}, "BLACKBOX_query_count": 3, "production_authority": False, "fresh_oos": False, "horizon_selected": False, "signal_refitted": False, "control_rematched": False, "option_outcomes_read": False, "formal_causal_inference": False}
    output.mkdir(parents=True, exist_ok=True)
    anchors = []
    for symbol, carrier in CARRIERS.items():
        block = pairs.loc[pairs.symbol == symbol].copy()
        if len(block) != COUNTS[symbol]:
            raise AdmissionError("frozen R1_A pair count mismatch")
        start = "2015-01-05" if symbol == "000852.SH" else "2020-07-23"
        frame = load_market_data(symbol, "1m", start, "2025-12-31", root=root)
        times = pd.DatetimeIndex(frame.market_time_shanghai)
        if not times.is_monotonic_increasing or times.has_duplicates:
            raise AdmissionError("invalid index observation clock")
        anchors.append(pair_clock(block, times, carrier))
        info = {"index": symbol, "frozen_pairs": len(block), "index_rows_verified": len(frame), "ETF_outcomes_read": False}
        receipt["carriers"][carrier] = info
        try:
            tape, actions, admission = admit(root, manifest_dir/(carrier+".json"), carrier, times)
            info["admission"] = admission
            audit, aligned, coverage = common_pairs(block, times, tape, actions)
            audit.to_csv(output/(carrier+"_coverage.csv"), index=False)
            info["common_sample"] = coverage
            if not coverage["minimum_coverage_pass"]:
                info["status"] = "INSUFFICIENT_CARRIER_COVERAGE_NO_OUTCOMES_OPENED"
                continue
            eligible = block.loc[block.pair_id.isin(audit.loc[audit.eligible, "pair_id"])]
            outcomes = measure(eligible, frame.close.to_numpy(float), aligned)
            outcomes.to_csv(output/(carrier+"_transport.csv"), index=False)
            info.update({"status": "TRANSPORT_MEASURED_DESCRIPTIVE_ONLY", "ETF_outcomes_read": True, "summary": summarize(outcomes)})
        except (AdmissionError, KeyError, ValueError, OSError) as exc:
            info["status"] = "BLOCKED_CARRIER_DATA_NOT_ADMITTED"
            info["reason"] = str(exc)
    anchor_frame = pd.concat(anchors, ignore_index=True)
    anchor_frame.to_csv(output/"frozen_index_clock_anchors.csv", index=False)
    receipt["anchor_rows"] = len(anchor_frame)
    receipt["unique_carrier_timestamps"] = int(anchor_frame[["carrier", "timestamp"]].drop_duplicates().shape[0])
    measured = sum(x["ETF_outcomes_read"] for x in receipt["carriers"].values())
    receipt["decision"] = "CARRIER_TRANSPORT_COMPLETE_DESCRIPTIVE" if measured == 2 else "PARTIAL_CARRIER_TRANSPORT" if measured else "BLOCKED_CARRIER_DATA_NOT_ADMITTED"
    receipt["ETF_outcomes_read"] = bool(measured)
    receipt["evidence_files"] = [{"path": p.name, "sha256": digest(p), "bytes": p.stat().st_size} for p in sorted(output.glob("*.csv"))]
    dump(output/"transport_receipt.json", receipt)
    return receipt

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--output", type=Path)
    ap.add_argument("--manifest-dir", type=Path)
    args = ap.parse_args(); root = args.root.resolve()
    output = args.output or root/"docs/ops/evidence/r1a_carrier_transport_20260912"
    manifests = args.manifest_dir or root/"data/r1a_carrier_prices"
    receipt = run(root, output, manifests)
    print(json.dumps({"decision": receipt["decision"], "ETF_outcomes_read": receipt["ETF_outcomes_read"], "carriers": {k: v["status"] for k,v in receipt["carriers"].items()}}, indent=2))
    return 0 if receipt["decision"] == "CARRIER_TRANSPORT_COMPLETE_DESCRIPTIVE" else 2

if __name__ == "__main__":
    raise SystemExit(main())
