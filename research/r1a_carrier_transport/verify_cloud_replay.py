"""Acceptance audit for 9abe704 cloud_pack_v1, not a new strategy experiment.

Read actual public ETF CSVs, verify their private-export lineage hashes, rerun
unchanged transport, and reconcile with the retained local result. The primary
carrier remains outcome-blocked. No local DataHub or private directory is used.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from research.r1a_carrier_transport import transport as tr
from research.r1a_carrier_transport.audit_public_delivery import compare_json, require, sha, read_csv

DELIVERY = "9abe7046e50b5eeb6299848eccf6039f7af55647"
PACK = "data/r1a_carrier_prices/cloud_pack_v1"
LOCAL = "docs/ops/evidence/r1a_carrier_transport_20260912_local"
SOURCE = "docs/ops/evidence/r1a_carrier_source_audit_20260912/source_delivery_audit.json"
FREEZE_SHA = "7c3b08847a873132df36c97b4c8c8e84c251c4b9c56568260ffbbb90ce99142b"


def coverage_counts(times: pd.DatetimeIndex, tape: pd.DataFrame) -> dict:
    """Disjoint observation categories, not a claim of exchange trade absence."""
    aligned = tape.reindex(times)
    present = np.asarray(times.isin(tape.index))
    vol = aligned.volume.to_numpy(float)
    numeric = aligned[["open", "high", "low", "close"]].to_numpy(float)
    valid_px = np.isfinite(numeric).all(axis=1) & (numeric > 0).all(axis=1)
    valid_vol = np.isfinite(vol) & (vol >= 0)
    zero = present & valid_px & valid_vol & (vol == 0)
    positive = present & valid_px & valid_vol & (vol > 0)
    invalid = present & ~(valid_px & valid_vol)
    missing = ~present
    require(int(missing.sum()+zero.sum()+positive.sum()+invalid.sum()) == len(times), "coverage categories not exhaustive")
    return {
        "expected_minutes": len(times), "present_minutes": int(present.sum()),
        "missing_minutes": int(missing.sum()), "recorded_zero_volume_minutes": int(zero.sum()),
        "positive_volume_minutes": int(positive.sum()), "invalid_present_minutes": int(invalid.sum()),
        "record_coverage": float(present.mean()) if len(times) else None,
        "positive_volume_coverage": float(positive.mean()) if len(times) else None,
    }


def compare_frames(actual: pd.DataFrame, expected: pd.DataFrame, keys: list[str]) -> dict:
    """Exact identities/categories; only floating roundoff is tolerated."""
    require(set(actual.columns) == set(expected.columns), "frame schema mismatch")
    require(len(actual) == len(expected), "frame row count mismatch")
    require(not actual.duplicated(keys).any() and not expected.duplicated(keys).any(), "duplicate comparison keys")
    a = actual.sort_values(keys).reset_index(drop=True)
    b = expected.sort_values(keys).reset_index(drop=True)
    errors = {}
    for col in b.columns:
        if pd.api.types.is_numeric_dtype(b[col]) and not pd.api.types.is_bool_dtype(b[col]):
            av = a[col].to_numpy(float); bv = b[col].to_numpy(float)
            require(np.isfinite(av).all() and np.isfinite(bv).all(), "nonfinite comparison: "+col)
            err = float(np.max(np.abs(av-bv))) if len(av) else 0.0
            require(err <= 1e-12, "numeric replay mismatch: "+col)
            errors[col] = err
        else:
            require(a[col].equals(b[col]), "identity/category replay mismatch: "+col)
    return {"rows": len(a), "maximum_absolute_errors": errors}


def verify(root: Path, output: Path) -> dict:
    from regime_lab.market_data import load_market_data
    require(not output.exists(), "new output directory required; do not overwrite evidence")
    require(not (root/"data/r1a_carrier_prices/private").exists(), "audit requires checkout WITHOUT private directory")
    require(sha(root/tr.FREEZE_PATH) == FREEZE_SHA, "frozen protocol changed")
    checklist = json.loads((root/PACK/"DELIVERY_CHECKLIST.json").read_text())
    source = json.loads((root/SOURCE).read_text())
    old_receipt = json.loads((root/LOCAL/"transport_receipt.json").read_text())
    checked, monthly, annual = [], [], {}
    primary_tape = primary_times = None
    mappings = {"expected_minutes":"index_minutes_expected", "present_minutes":"present_on_index_clock", "missing_minutes":"completely_missing_on_index_clock", "recorded_zero_volume_minutes":"present_zero_volume", "positive_volume_minutes":"present_positive_volume"}
    for index_symbol, carrier in tr.CARRIERS.items():
        m = json.loads((root/PACK/(carrier+".json")).read_text())
        prior = json.loads((root/"data/r1a_carrier_prices"/(carrier+".json")).read_text())
        declared = checklist["carriers"][carrier]
        require(sha(root/PACK/(carrier+".json")) == declared["manifest_sha256"], "manifest/checklist hash mismatch")
        compare_json(m["files"], declared["files"], carrier+".checklist.files")
        compare_json(m["corporate_actions_file"], declared["corporate_actions_file"], carrier+".checklist.actions")
        specs = m["files"]+[m["corporate_actions_file"]]
        old_specs = prior["files"]+[prior["corporate_actions_file"]]
        require(len(specs)==len(old_specs)==6, "expected five annual price CSVs and one action CSV per carrier")
        frames = []
        for spec, old in zip(specs,old_specs,strict=True):
            rel = Path(spec["path"])
            require(rel.is_relative_to(PACK+"/prices") and not (root/rel).is_symlink(), "data path outside public pack or symlink")
            for k in ("sha256","bytes","rows"):
                require(spec[k]==old[k], "private-export lineage changed: "+str(rel))
            frame, file_info = tr.checked_csv(root,spec)
            checked.append({"carrier":carrier, **file_info})
            if spec is not specs[-1]:
                frames.append(frame)
        tape = tr.validate_prices(pd.concat(frames,ignore_index=True),carrier)
        require(len(tape)==declared["total_rows"], "price row total differs")
        start = "2015-01-05" if index_symbol=="000852.SH" else "2020-07-23"
        index = load_market_data(index_symbol,"1m",start,"2025-12-31",root=root)
        times = pd.DatetimeIndex(index.market_time_shanghai)
        annual[carrier] = {}
        for year in tr.YEARS:
            target = times[times.year==int(year)]
            counts = coverage_counts(target,tape)
            for k, old_k in mappings.items():
                require(counts[k]==source["carriers"][carrier][year][old_k], "source audit count differs: "+carrier+year+k)
            require(counts["invalid_present_minutes"]==0, "invalid price/volume on reference clock")
            counts["missing_by_date"] = {str(k):int(v) for k,v in pd.Series(target[~target.isin(tape.index)].strftime("%Y-%m-%d"),dtype=str).value_counts().sort_index().items()}
            annual[carrier][year] = counts
            for month in range(1,13):
                month_times = target[target.month==month]
                monthly.append({"carrier":carrier,"index_symbol":index_symbol,"month":f"{year}-{month:02d}",**coverage_counts(month_times,tape)})
        if carrier=="512100.SH":
            primary_tape,primary_times = tape,times
    require(len(checked)==12, "expected exactly twelve actual CSV files")
    require(set((root/PACK/"prices").glob("*.csv"))=={root/x["path"] for x in checked}, "unlisted/missing CSV in pack")
    output.mkdir(parents=True)
    pd.DataFrame(monthly).to_csv(output/"monthly_observation_coverage.csv",index=False)
    # Existing 95% annual gate and full pair rules are NOT modified or bypassed.
    replay = tr.run(root,output/"replay",root/PACK)
    require(replay["decision"]=="PARTIAL_CARRIER_TRANSPORT", "unexpected replay decision")
    primary = replay["carriers"]["512100.SH"]
    require(primary["ETF_outcomes_read"] is False, "blocked primary outcome was opened")
    require(primary["reason"].startswith("INSUFFICIENT_CARRIER_MINUTE_COVERAGE "), "unexpected primary blocker")
    require(not (output/"replay/512100.SH_transport.csv").exists(), "primary outcome ledger must not exist")
    prefix = "INSUFFICIENT_CARRIER_MINUTE_COVERAGE "
    compare_json(json.loads(primary["reason"][len(prefix):]),json.loads(old_receipt["carriers"]["512100.SH"]["reason"][len(prefix):]),"primary.coverage")
    secondary = replay["carriers"]["588000.SH"]
    require(secondary["ETF_outcomes_read"] is True, "secondary replay did not run")
    reconciled = {}
    old_files={s["path"]:s for s in old_receipt["evidence_files"]}
    for filename,keys in [("588000.SH_coverage.csv",["pair_id"]),("588000.SH_transport.csv",["pair_id","horizon"])]:
        previous=root/LOCAL/filename; fresh=output/"replay"/filename
        require(sha(previous)==old_files[filename]["sha256"] and previous.stat().st_size==old_files[filename]["bytes"], "old evidence changed")
        reconciled[filename] = compare_frames(read_csv(fresh),read_csv(previous),keys)
        reconciled[filename]["byte_identical"] = sha(fresh)==sha(previous)
    leaves=compare_json(secondary["summary"],old_receipt["carriers"]["588000.SH"]["summary"],"secondary.summary")
    compare_json(secondary["common_sample"],old_receipt["carriers"]["588000.SH"]["common_sample"],"secondary.common_sample")
    # Availability-only diagnostic uses the same existing pair/path rule. No returns.
    pairs=read_csv(root/tr.PAIRS_PATH)
    pairs=pairs.loc[(pairs.cell=="R1_A") & (pairs.symbol=="000852.SH")].copy()
    pairs["pair_id"]=pairs.symbol+":R1_A:"+pairs.event_entry_idx.astype(str)+":"+pairs.control_entry_idx.astype(str)
    actions=read_csv(root/PACK/"prices/512100_actions.csv")
    path_coverage,_,path_stats=tr.common_pairs(pairs,primary_times,primary_tape,sorted(set(actions.ex_date.astype(str))))
    path_coverage.to_csv(output/"512100_frozen_path_availability_ONLY.csv",index=False)
    report={
        "schema_id":"factorlab_r1a_cloud_raw_replay_acceptance@1.0",
        "decision":"PUBLIC_CSV_DELIVERY_VERIFIED_SECONDARY_RAW_REPLAY_REPRODUCED",
        "delivery_commit":DELIVERY,
        "verification_code_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),
        "github_run_id":__import__("os").environ.get("GITHUB_RUN_ID"),
        "freeze_sha256":FREEZE_SHA,
        "private_directory_present":False,"DataHub_used":False,
        "actual_csv_files_verified":len(checked),"annual_price_csv_count":10,"corporate_action_csv_count":2,
        "total_csv_bytes":sum(s["bytes"] for s in checked),"total_price_rows":sum(v["total_rows"] for v in checklist["carriers"].values()),
        "verified_files":checked,"annual_observation_coverage":annual,
        "primary_frozen_pair_path_availability_ONLY":path_stats,
        "primary_outcomes_read":False,
        "secondary_raw_canonical_ETF_prices_replayed":True,
        "secondary_complete_pairs":secondary["common_sample"]["complete_pairs"],
        "reconciliation":reconciled,"summary_leaves_reconciled":leaves,
        "research_state":replay["decision"],
        "upstream_DataHub_raw_to_canonical_reexport_performed":False,
        "exchange_no_trade_independently_verified":False,
        "source_limitations":["Zero-volume means the delivered source records volume=0; exchange no-trade versus vendor placeholder is not independently established.","Delivered canonical OHLCV is now cloud-readable and replayed; upstream dictionary/corporate-action source snapshots remain referenced by the local audit rather than re-downloaded here."],
        "BLACKBOX_query_count":3,"production_authority":False,"fresh_oos":False,
        "horizon_selected":False,"signal_refitted":False,"control_rematched":False,
    }
    lines=["# R1_A public CSV delivery — independent cloud replay", "", "Decision: `"+report["decision"]+"`", "", "Delivery commit: `"+DELIVERY+"`", "", f"Verified {len(checked)} actual CSVs: 10 annual OHLCV and 2 corporate-action tables; {report['total_price_rows']:,} price rows; {report['total_csv_bytes']:,} bytes. No private directory or local DataHub was used.", "", "## Reproduction", "", f"588000: {report['secondary_complete_pairs']}/1802 complete pairs; all seven horizons regenerated from actual canonical ETF CSVs and original index bytes. {leaves} nested summary values reconciled with the local receipt.", "", "| Ledger | Rows | Byte-identical | Max numeric error |", "|---|---:|---|---:|"]
    for name,x in reconciled.items():
        lines.append(f"| {name} | {x['rows']} | {x['byte_identical']} | {max(x['maximum_absolute_errors'].values(),default=0):.3g} |")
    lines += ["", "## Primary coverage — no return measurement", "", "| Year | Expected | Missing | Recorded zero volume | Positive volume | Valid coverage |", "|---|---:|---:|---:|---:|---:|"]
    for year,x in annual["512100.SH"].items():
        lines.append(f"| {year} | {x['expected_minutes']} | {x['missing_minutes']} | {x['recorded_zero_volume_minutes']} | {x['positive_volume_minutes']} | {x['positive_volume_coverage']:.6%} |")
    lines += ["", "The 2021 95% gate still fails. No primary returns, year removal, zero-volume filling, ETF substitution or gate relaxation occurred.", "", "For data-quality diagnosis only, the existing common 240-bar event-and-control path rule gives:", "", "```json",json.dumps(path_stats,ensure_ascii=False,indent=2),"```", "", "These availability counts are NOT returns or permission to bypass admission.","", "## Source boundary", "", *["- "+s for s in report["source_limitations"]], "", "Research state remains `PARTIAL_CARRIER_TRANSPORT`. File-delivery acceptance and computational reproduction do not grant causal, significance, fresh-OOS or trading-profitability claims. `BLACKBOX_query_count=3`; `production_authority=false`."]
    (output/"REPORT.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    report["evidence_files"]=[{"path":str(p.relative_to(output)),"sha256":sha(p),"bytes":p.stat().st_size} for p in sorted(output.rglob("*")) if p.is_file()]
    tr.dump(output/"acceptance_receipt.json",report)
    return report


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=verify(args.root.resolve(),args.output.resolve())
    print(json.dumps({k:result[k] for k in ("decision","actual_csv_files_verified","total_price_rows","reconciliation","primary_outcomes_read","research_state")},indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
