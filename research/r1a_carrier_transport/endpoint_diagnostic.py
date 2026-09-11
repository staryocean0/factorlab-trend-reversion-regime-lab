"""Separate endpoint-conditional price diagnostic; never rewrites full-path v1.

Synthetic tests precede outcome release. Original signals/pairs and all horizons
are fixed. Positive-volume EXACT endpoints remain mandatory; interiors are not
used to compute terminal returns. No path risk or executable-PnL claim is made.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

HORIZONS = (1, 5, 15, 30, 60, 120, 240)
YEARS = tuple(str(y) for y in range(2021, 2026))
MAP = {"000852.SH": "512100.SH", "000688.SH": "588000.SH"}
COUNTS = {"000852.SH": 1296, "000688.SH": 1802}
PACK = "data/r1a_carrier_prices/cloud_pack_v1"
FREEZE = "docs/governance/R1A_ENDPOINT_PRICE_DIAGNOSTIC_FREEZE@1.0.json"
FREEZE_COMMIT = "6687f9fa7000e02b03a0d5a7a4a65d9a63359116"
METRICS = ("etf_event", "etf_control", "etf_incremental", "index_event", "index_control", "index_incremental", "event_tracking_residual", "incremental_tracking_residual")
FEATURES = ("parent_abs_drift", "parent_efficiency", "log1p_parent_age_bars", "local_vol_30_over_240")

class EndpointError(ValueError):
    """An input, identity, or methodological boundary was violated."""

def require(ok: bool, message: str) -> None:
    if not ok:
        raise EndpointError(message)

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")

def coverage_gate(audit: pd.DataFrame) -> dict:
    require(not audit.pair_id.duplicated().any(), "duplicate coverage pair")
    require(audit.eligible.isin([True, False]).all(), "invalid eligibility flag")
    counts = {"pooled": {"eligible": int(audit.eligible.sum()), "total": len(audit)}}
    for year in YEARS:
        block = audit.loc[audit.event_day.astype(str).str.startswith(year)]
        counts[year] = {"eligible": int(block.eligible.sum()), "total": len(block)}
    rates = {k: v["eligible"] / v["total"] if v["total"] else 0.0 for k, v in counts.items()}
    return {"counts": counts, "coverage": rates, "minimum": 0.80,
            "pass": all(v >= 0.80 for v in rates.values())}

def endpoint_availability(pairs: pd.DataFrame, times: pd.DatetimeIndex,
                          tape: pd.DataFrame, ex_dates: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    require(times.is_monotonic_increasing and not times.has_duplicates, "invalid index clock")
    require(not pairs.pair_id.duplicated().any(), "duplicate original pair")
    require(not tape.index.has_duplicates, "duplicate ETF clock")
    aligned = tape.reindex(times)  # default: missing stays NaN, never ffill or nearest
    prices = aligned.close.to_numpy(float)
    volume = aligned.volume.to_numpy(float)
    days = np.asarray(times.strftime("%Y-%m-%d"))
    present = np.asarray(times.isin(tape.index))
    ex = np.asarray(ex_dates, dtype=str)
    records = []
    for p in pairs.itertuples(index=False):
        require(int(p.parent_direction) in (-1, 1), "bad direction")
        e, c = int(p.event_entry_idx), int(p.control_entry_idx)
        require(min(e, c) >= 0 and max(e, c) + max(HORIZONS) < len(times), "out-of-range pair")
        require(p.side == ("LONG" if p.parent_direction == 1 else "SHORT"), "side changed")
        for h in HORIZONS:
            row = {"pair_id": p.pair_id, "index_symbol": p.symbol, "event_day": p.event_day,
                   "control_day": p.control_day, "side": p.side, "horizon": h}
            reasons = []
            for leg, a in (("event", e), ("control", c)):
                b = a + h
                for point, i in (("entry", a), ("exit", b)):
                    key = leg + "_" + point
                    row[key + "_timestamp"] = times[i].isoformat()
                    if not present[i]:
                        status = "missing"
                    elif not np.isfinite(prices[i]) or prices[i] <= 0 or not np.isfinite(volume[i]) or volume[i] < 0:
                        status = "invalid"
                    elif volume[i] == 0:
                        status = "recorded_zero_volume"
                    else:
                        status = "valid"
                    row[key + "_status"] = status
                    if status != "valid":
                        reasons.append(key + ":" + status)
                crossing = bool(len(ex) and np.any((ex > days[a]) & (ex <= days[b])))
                row[leg + "_action_crossing"] = crossing
                if crossing:
                    reasons.append(leg + ":corporate_action_crossing")
            row["eligible"] = not reasons
            row["reason"] = ";".join(reasons) or "four_exact_observed_endpoints"
            records.append(row)
    return pd.DataFrame(records), prices

def index_returns(pairs: pd.DataFrame, prices: np.ndarray, h: int) -> pd.DataFrame:
    e, c = pairs.event_entry_idx.to_numpy(int), pairs.control_entry_idx.to_numpy(int)
    d = pairs.parent_direction.to_numpy(int)
    require(np.isin(d, [-1, 1]).all(), "invalid direction")
    required = prices[np.r_[e, e+h, c, c+h]]
    require(np.isfinite(required).all() and (required > 0).all(), "invalid index endpoints")
    out = pairs[["pair_id", "symbol", "event_day", "control_day", "side"]].reset_index(drop=True).copy()
    out["horizon"] = h
    out["index_event"] = d * (prices[e+h]/prices[e] - 1)
    out["index_control"] = d * (prices[c+h]/prices[c] - 1)
    out["index_incremental"] = out.index_event - out.index_control
    return out

def measure_endpoints(pairs: pd.DataFrame, index_px: np.ndarray,
                      etf_px: np.ndarray, h: int) -> pd.DataFrame:
    require(h in HORIZONS, "unfrozen horizon")
    out = index_returns(pairs, index_px, h)
    e, c = pairs.event_entry_idx.to_numpy(int), pairs.control_entry_idx.to_numpy(int)
    d = pairs.parent_direction.to_numpy(int)
    required = etf_px[np.r_[e, e+h, c, c+h]]
    require(np.isfinite(required).all() and (required > 0).all(), "invalid ETF endpoints")
    out["etf_event"] = d * (etf_px[e+h]/etf_px[e] - 1)
    out["etf_control"] = d * (etf_px[c+h]/etf_px[c] - 1)
    out["etf_incremental"] = out.etf_event - out.etf_control
    out["event_tracking_residual"] = out.etf_event - out.index_event
    out["incremental_tracking_residual"] = out.etf_incremental - out.index_incremental
    return out

def distribution(series: pd.Series) -> dict:
    x = series.to_numpy(float)
    require(np.isfinite(x).all(), "nonfinite return")
    if not len(x):
        return {"n": 0, "mean_bp": None, "median_bp": None, "positive_fraction": None,
                "zero_fraction": None, "std_bp": None, "q10_bp": None, "q90_bp": None}
    return {"n": len(x), "mean_bp": float(x.mean()*1e4), "median_bp": float(np.median(x)*1e4),
            "positive_fraction": float((x > 0).mean()), "zero_fraction": float((x == 0).mean()),
            "std_bp": float(x.std()*1e4), "q10_bp": float(np.quantile(x, .1)*1e4),
            "q90_bp": float(np.quantile(x, .9)*1e4)}

def describe(frame: pd.DataFrame) -> dict:
    out = {k: distribution(frame[k]) for k in METRICS}
    correlation = frame.etf_event.corr(frame.index_event) if len(frame) > 1 and frame.etf_event.std() > 0 and frame.index_event.std() > 0 else np.nan
    out["event_return_correlation"] = float(correlation) if np.isfinite(correlation) else None
    return out

def summarize(frame: pd.DataFrame) -> dict:
    return {"pooled": describe(frame),
            "sides": {s: describe(frame.loc[frame.side == s]) for s in ("LONG", "SHORT")},
            "years": {y: describe(frame.loc[frame.event_day.astype(str).str.startswith(y)]) for y in YEARS}}

def selection_audit(pairs: pd.DataFrame, ix: pd.DataFrame, chosen: set[str]) -> dict:
    out = {}
    for group, mask in (("all", np.ones(len(pairs), bool)),
                        ("eligible", pairs.pair_id.isin(chosen).to_numpy()),
                        ("excluded", ~pairs.pair_id.isin(chosen).to_numpy())):
        p = pairs.loc[mask]
        returns = ix.loc[ix.pair_id.isin(set(p.pair_id))]
        features = {}
        for leg in ("event", "control"):
            for f in FEATURES:
                name = leg + "_" + f
                if name in pairs:
                    features[name] = float(p[name].mean()) if len(p) else None
        if "match_distance" in p:
            features["match_distance"] = float(p.match_distance.mean()) if len(p) else None
        out[group] = {"n": len(p), "side_counts": {s: int((p.side == s).sum()) for s in ("LONG", "SHORT")},
                      "year_counts": {y: int(p.event_day.astype(str).str.startswith(y).sum()) for y in YEARS},
                      "feature_means": features,
                      "index": {k: distribution(returns[k]) for k in ("index_event", "index_control", "index_incremental")}}
    return out

def analyse(pairs: pd.DataFrame, times: pd.DatetimeIndex, index_px: np.ndarray,
            tape: pd.DataFrame, ex_dates: list[str], record_gate: bool = True) -> tuple[dict, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    audit, etf_px = endpoint_availability(pairs, times, tape, ex_dates)
    common_flags = audit.groupby("pair_id", sort=False).eligible.all()
    common_audit = pairs[["pair_id", "event_day", "side"]].copy()
    common_audit["eligible"] = common_audit.pair_id.map(common_flags)
    common_gate = coverage_gate(common_audit)
    common_ids = set(common_audit.loc[common_audit.eligible, "pair_id"])
    common_gate["source_record_gate_pass"] = bool(record_gate)
    common_gate["outcomes_measured"] = bool(record_gate and common_gate["pass"])
    result = {"horizons": {}, "common_endpoint_sensitivity": {"gate": common_gate, "horizons": {}}}
    ledgers, common_ledgers = [], []
    # All per-horizon outcome gates are determined from availability, before any ETF returns.
    gates = {h: coverage_gate(audit.loc[audit.horizon == h]) for h in HORIZONS}
    for h in HORIZONS:
        a = audit.loc[audit.horizon == h]
        ids = set(a.loc[a.eligible, "pair_id"])
        gate = gates[h]
        info = {"gate": gate, "reasons": {str(k): int(v) for k, v in a.reason.value_counts().items()},
                "status": "INSUFFICIENT_ENDPOINT_COVERAGE", "ETF_outcomes_read": False,
                "composition": selection_audit(pairs, index_returns(pairs, index_px, h), ids)}
        result["horizons"][str(h)] = info
        if record_gate and gate["pass"]:
            ledger = measure_endpoints(pairs.loc[pairs.pair_id.isin(ids)], index_px, etf_px, h)
            info.update({"status": "MEASURED_CONDITIONAL_DESCRIPTIVE_ONLY", "ETF_outcomes_read": True,
                         "summary": summarize(ledger)})
            ledgers.append(ledger)
        elif not record_gate:
            info["status"] = "INSUFFICIENT_SOURCE_RECORD_COVERAGE"
        if common_gate["outcomes_measured"]:
            common = measure_endpoints(pairs.loc[pairs.pair_id.isin(common_ids)], index_px, etf_px, h)
            result["common_endpoint_sensitivity"]["horizons"][str(h)] = summarize(common)
            common_ledgers.append(common)
    return (result, audit, pd.concat(ledgers, ignore_index=True) if ledgers else pd.DataFrame(),
            pd.concat(common_ledgers, ignore_index=True) if common_ledgers else pd.DataFrame())

def load_tape(root: Path, symbol: str, times: pd.DatetimeIndex, checklist: dict) -> tuple[pd.DataFrame, list[str], dict]:
    from research.r1a_carrier_transport import transport as tr
    path = root/PACK/(symbol + ".json")
    declared = checklist["carriers"][symbol]
    require(sha(path) == declared["manifest_sha256"], "manifest identity changed")
    m = json.loads(path.read_text())
    exact = {"symbol": symbol, "frequency": "1m", "timezone": "Asia/Shanghai", "bar_label": "bar_end",
             "price_basis": "unadjusted_actual_traded_OHLC", "volume_unit": "shares",
             "zero_volume_semantics": "not_an_observed_trade", "research_use_authorized": True,
             "corporate_actions_complete": True, "corporate_actions_window": tr.WINDOW}
    for k, v in exact.items():
        require(type(m.get(k)) is type(v) and m[k] == v, "source contract drift: " + k)
    require(m["files"] == declared["files"] and m["corporate_actions_file"] == declared["corporate_actions_file"], "checklist drift")
    frames, verified = [], []
    for s in m["files"] + [m["corporate_actions_file"]]:
        rel = Path(s["path"])
        require(rel.is_relative_to(PACK + "/prices") and not (root/rel).is_symlink(), "not a real pinned public file")
        frame, metadata = tr.checked_csv(root, s)
        verified.append(metadata)
        if s == m["corporate_actions_file"]:
            actions = frame
        else:
            frames.append(frame)
    require(len(frames) == 5 and len(verified) == 6, "expected six CSVs per carrier")
    tape = tr.validate_prices(pd.concat(frames, ignore_index=True), symbol)
    require(len(tape) == declared["total_rows"], "price count drift")
    require({"symbol", "ex_date", "event_type", "source_reference"}.issubset(actions.columns), "action schema")
    dates = []
    if len(actions):
        require(actions.symbol.eq(symbol).all() and not actions.isna().any().any(), "action identity/completeness")
        dates = sorted(set(pd.to_datetime(actions.ex_date, format="%Y-%m-%d", errors="raise").dt.strftime("%Y-%m-%d")))
        require(all("2021-01-01" <= d <= "2025-12-31" for d in dates), "action window drift")
    annual = {}
    for year in YEARS:
        t = times[times.year == int(year)]
        require(len(t) > 0, "missing index year")
        aligned = tape.reindex(t)
        present = np.asarray(t.isin(tape.index))
        zero = aligned.volume.to_numpy(float) == 0
        positive = aligned.volume.to_numpy(float) > 0
        annual[year] = {"expected": len(t), "present": int(present.sum()), "missing": int((~present).sum()),
                        "recorded_zero_volume": int(zero.sum()), "positive_volume": int(positive.sum()),
                        "record_coverage": float(present.mean()), "positive_volume_coverage": float(positive.mean())}
    return tape, dates, {"manifest_sha256": sha(path), "files": verified, "annual_observations": annual,
                         "record_coverage_gate_pass": all(v["record_coverage"] >= .95 for v in annual.values()),
                         "source_semantics": "Inherited delivered canonical metadata; not fresh independent exchange verification."}

def f(value: Any) -> str:
    return "NA" if value is None else f"{value:+.3f}"

def report(receipt: dict) -> str:
    lines = ["# R1_A observed-endpoint price diagnostic", "", f"Decision: `{receipt['decision']}`", "",
             "This is a separate retrospective endpoint-conditional estimand. Original full-path v1 remains PARTIAL_CARRIER_TRANSPORT; no v1 gate or prior receipt was edited.", "",
             f"Freeze commit: `{FREEZE_COMMIT}`; code commit: `{receipt['code_commit']}`.", "",
             "Four positive-volume exact endpoints per pair/horizon remain mandatory. Interiors do not enter terminal-return algebra. No missing price is filled; no 2021 removal; no signal/control refit. Exit-availability conditioning is NOT a live entry rule."]
    for carrier, info in receipt["carriers"].items():
        lines += ["", "## " + carrier, "", "| h | included/all | pooled coverage | worst-year coverage | ETF event bp | ETF control bp | ETF increment bp | same-sample index increment bp | increment residual bp | corr |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for h, x in info["horizons"].items():
            g = x["gate"]; c = g["counts"]["pooled"]
            prefix = f"| {h} | {c['eligible']}/{c['total']} | {g['coverage']['pooled']:.2%} | {min(g['coverage'][y] for y in YEARS):.2%} |"
            if not x["ETF_outcomes_read"]:
                lines.append(prefix + " NA | NA | NA | NA | NA | NA |")
                continue
            p = x["summary"]["pooled"]
            lines.append(prefix + " " + " | ".join(f(p[k]["mean_bp"]) for k in ("etf_event", "etf_control", "etf_incremental", "index_incremental", "incremental_tracking_residual")) + " | " + f(p["event_return_correlation"]) + " |")
        lines += ["", "### Side, year and selection diagnostics", "", "| h | LONG increment bp | SHORT increment bp | positive increment years | ETF event median bp | ETF event positive fraction | full-index increment bp | eligible-index increment bp | excluded-index increment bp |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
        for h, x in info["horizons"].items():
            comp = x["composition"]
            tail = " | ".join(f(comp[g]["index"]["index_incremental"]["mean_bp"]) for g in ("all", "eligible", "excluded"))
            if not x["ETF_outcomes_read"]:
                lines.append(f"| {h} | NA | NA | NA | NA | NA | {tail} |")
                continue
            s = x["summary"]; p = s["pooled"]
            npos = sum((v["etf_incremental"]["mean_bp"] or 0) > 0 for v in s["years"].values())
            lines.append(f"| {h} | {f(s['sides']['LONG']['etf_incremental']['mean_bp'])} | {f(s['sides']['SHORT']['etf_incremental']['mean_bp'])} | {npos}/5 | {f(p['etf_event']['median_bp'])} | {p['etf_event']['positive_fraction']:.2%} | {tail} |")
        common = info["common_endpoint_sensitivity"]; cg = common["gate"]
        lines += ["", f"Common-endpoint intersection: {cg['counts']['pooled']['eligible']}/{cg['counts']['pooled']['total']}; gate pass={cg['pass']}; outcomes measured={cg['outcomes_measured']}.", "", "Annual common-endpoint coverage: `" + json.dumps(cg["coverage"]) + "`."]
        if cg["outcomes_measured"]:
            lines += ["", "| common-sample h | ETF event bp | ETF increment bp | same-sample index increment bp |", "|---:|---:|---:|---:|"]
            for h, s in common["horizons"].items():
                p = s["pooled"]
                lines.append(f"| {h} | {f(p['etf_event']['mean_bp'])} | {f(p['etf_incremental']['mean_bp'])} | {f(p['index_incremental']['mean_bp'])} |")
    lines += ["", "## Interpretation boundary", "",
              "All seven horizons and both fixed carriers are reported, including unavailable cells. Per-horizon primary samples can differ. Use the composition audit and gated common-sample sensitivity before comparing horizon means; do not choose a winner.", "",
              "Coverage is a reporting safeguard, not proof that missingness is random. ETF returns for excluded pairs remain unknown. These observed historical samples do not establish all-event alpha, causal identification, fresh OOS, statistical significance, net profits, borrow feasibility, or complete-path risk.", "",
              "Source-recorded zero volume is not independently verified exchange no-trade. Canonical source time/corporate-action assumptions are inherited. No new upstream data was invented.", "",
              "No MFE/MAE, stops or targets were computed. No BLACKBOX query #4. production_authority=false; fresh_oos=false."]
    return "\n".join(lines) + "\n"

def run(root: Path, output: Path) -> dict:
    from regime_lab.market_data import load_market_data
    from research.r1a_carrier_transport import transport as tr
    require(not output.exists(), "fresh output directory required")
    tr.assert_blob(root/FREEZE, "d83d0d859c1cdfa60a86768f7dfdb5f0a40f8809")
    freeze = json.loads((root/FREEZE).read_text())
    require(freeze["status"] == "FROZEN_BEFORE_NEW_ENDPOINT_OUTCOMES", "protocol status drift")
    require(freeze["inputs"]["horizons"] == list(HORIZONS) and freeze["inputs"]["carriers"] == MAP, "scope drift")
    require(freeze["inputs"]["expected_pairs"] == COUNTS, "count contract drift")
    require(freeze["data_integrity"]["minimum_record_coverage_each_year"] == .95 and freeze["sampling"]["minimum_pair_coverage_pooled_and_each_event_year"] == .80, "endpoint gate drift")
    require(freeze["measurements"]["BLACKBOX_query_count"] == 3 and not freeze["measurements"]["production_authority"] and not freeze["measurements"]["blackbox_query_4_authorized"], "governance drift")
    require(sha(root/tr.FREEZE_PATH) == freeze["inputs"]["old_freeze_sha256"], "original full-path freeze changed")
    tr.assert_blob(root/(PACK + "/DELIVERY_CHECKLIST.json"), freeze["inputs"]["checklist_git_blob_sha1"])
    tr.assert_blob(root/tr.PAIRS_PATH, tr.PAIRS_BLOB)
    tr.assert_blob(root/"data/manifest.json", tr.INDEX_BLOB)
    checklist = json.loads((root/PACK/"DELIVERY_CHECKLIST.json").read_text())
    pairs = pd.read_csv(root/tr.PAIRS_PATH)
    pairs = pairs.loc[pairs.cell == "R1_A"].copy()
    pairs["pair_id"] = pairs.symbol.astype(str) + ":R1_A:" + pairs.event_entry_idx.astype(str) + ":" + pairs.control_entry_idx.astype(str)
    require(not pairs.pair_id.duplicated().any(), "pair identity duplicate")
    receipt = {"schema_id": "factorlab_r1a_endpoint_diagnostic_receipt@1.0", "freeze_commit": FREEZE_COMMIT,
               "freeze_sha256": sha(root/FREEZE), "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
               "github_run_id": os.environ.get("GITHUB_RUN_ID"), "old_full_path_status": "PARTIAL_CARRIER_TRANSPORT_UNCHANGED",
               "carriers": {}, "BLACKBOX_query_count": 3, "production_authority": False, "fresh_oos": False,
               "horizon_selected": False, "signal_refitted": False, "control_rematched": False,
               "new_significance_test": False, "formal_causal_inference": False, "path_risk_measured": False,
               "estimator": "Retrospective observed-four-endpoint conditional paired terminal returns, not all-event or live-tradable effect."}
    output.mkdir(parents=True)
    for index_symbol, carrier in MAP.items():
        block = pairs.loc[pairs.symbol == index_symbol].copy()
        require(len(block) == COUNTS[index_symbol], "frozen pair count mismatch")
        start = "2015-01-05" if index_symbol == "000852.SH" else "2020-07-23"
        index = load_market_data(index_symbol, "1m", start, "2025-12-31", root=root)
        times = pd.DatetimeIndex(index.market_time_shanghai)
        tape, dates, integrity = load_tape(root, carrier, times, checklist)
        info, audit, ledger, common = analyse(block, times, index.close.to_numpy(float), tape, dates, integrity["record_coverage_gate_pass"])
        info["index_symbol"] = index_symbol
        info["source_integrity"] = integrity
        receipt["carriers"][carrier] = info
        audit.to_csv(output/(carrier + "_endpoint_availability.csv"), index=False)
        if len(ledger):
            ledger.to_csv(output/(carrier + "_endpoint_returns.csv"), index=False)
        if len(common):
            common.to_csv(output/(carrier + "_common_endpoint_returns.csv"), index=False)
        print(carrier, {h: {"coverage": x["gate"]["coverage"], "status": x["status"]} for h, x in info["horizons"].items()}, flush=True)
    measured = sum(x["ETF_outcomes_read"] for c in receipt["carriers"].values() for x in c["horizons"].values())
    receipt["measured_carrier_horizons"] = measured
    receipt["decision"] = "ENDPOINT_DIAGNOSTIC_COMPLETE_DESCRIPTIVE" if measured == 14 else "PARTIAL_ENDPOINT_DIAGNOSTIC" if measured else "ENDPOINT_DIAGNOSTIC_INSUFFICIENT_COVERAGE"
    receipt["evidence_files"] = [{"path": p.name, "sha256": sha(p), "bytes": p.stat().st_size} for p in sorted(output.glob("*.csv"))]
    dump(output/"endpoint_receipt.json", receipt)
    (output/"REPORT.md").write_text(report(receipt), encoding="utf-8")
    print(json.dumps({"decision": receipt["decision"], "measured_carrier_horizons": measured}))
    return receipt

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.root.resolve(), args.output)
    return 0  # success means diagnostic completed; see receipt for measured/blocked status

if __name__ == "__main__":
    raise SystemExit(main())
