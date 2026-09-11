"""Bounded acquisition audit; inspect metadata/timestamps, never strategy outcomes.

No login, purchase, secret enumeration, price imputation, or BLACKBOX evaluation.
The only optional credential is an already configured TUSHARE_TOKEN sent to the
provider's HTTPS endpoint. Raw provider bytes are not committed to public Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor

REPOS = (
    "factorlab-trend-reversion-regime-lab", "factorlab-two-wave-strategy-lab",
    "factorlab-star50-filter-lab", "factorlab-overnight-open-lab",
    "factorlab-multifactor-stock-lab",
)
START, END = "2021-01-01", "2025-12-31"
DOCS = {
    "akshare": "https://akshare.akfamily.xyz/data/fund/fund_public.html",
    "tushare": "https://tushare.pro/document/2?doc_id=387",
}

def fetch(url: str, payload: dict | None = None, *, github: bool = False) -> tuple[bytes, int]:
    headers = {"User-Agent": "FactorLab-R1A-carrier-acquisition-audit", "Accept": "application/json"}
    if github and os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    data = None
    if payload is not None:
        data = json.dumps(payload).encode(); headers["Content-Type"] = "application/json"
    with urlopen(Request(url, data=data, headers=headers), timeout=20) as r:
        raw = r.read(8*1024*1024+1)
        if len(raw) > 8*1024*1024:
            raise ValueError("response exceeds metadata-probe byte budget")
        return raw, r.status

def repository_inventory(repo: str) -> dict:
    url = f"https://api.github.com/repos/staryocean0/{repo}/git/trees/main?recursive=1"
    try:
        raw, status = fetch(url, github=True); data = json.loads(raw)
        tree = data["tree"]
        blobs = [x for x in tree if x["type"] == "blob" and x["path"].startswith("data/")]
        named = [x for x in blobs if re.search(r"512100|588000|159845|159629|159633|560010|588080|588050|588090|etf", x["path"], re.I) and re.search(r"\.(csv|parquet|feather|zip|gz|json)$", x["path"], re.I)]
        return {"repository": repo, "url": url, "tree_sha": data["sha"], "http_status": status, "truncated": bool(data.get("truncated")), "data_blob_count": len(blobs), "candidate_paths": [{"path": x["path"], "bytes": x.get("size"), "blob_sha1": x["sha"]} for x in named], "status": "CANDIDATE_PATHS_REQUIRE_ADMISSION" if named else "NO_ETF_NAMED_DATA_BLOBS", "limitation": "Default-branch path inventory only; not a claim about local disks, private repositories, artifacts, every branch or unlabeled binary files.", "response_sha256": hashlib.sha256(raw).hexdigest()}
    except Exception as exc:
        return {"repository": repo, "url": url, "status": "INVENTORY_UNAVAILABLE", "error_type": type(exc).__name__}

def timestamp_summary(rows: list[str]) -> dict:
    dates = sorted(str(x).split(",")[0] for x in rows)
    inside = [x for x in dates if START <= x[:10] <= END]
    return {"returned_rows": len(dates), "requested_window_rows": len(inside), "first_timestamp": dates[0] if dates else None, "last_timestamp": dates[-1] if dates else None, "out_of_window_rows": len(dates)-len(inside)}

def eastmoney_probe(code: str) -> dict:
    params = {"secid": "1."+code, "klt": "1", "fqt": "0", "beg": "20210101", "end": "20251231", "lmt": "8000", "fields1": "f1,f2,f3,f4,f5,f6", "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"}
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get?"+urlencode(params)
    result = {"source": "Eastmoney_bounded_historical_kline_capability_probe", "carrier": code+".SH", "url": url, "docs": DOCS["akshare"], "documented_1m_limit": "fund_etf_hist_min_em returns recent five trading days only; a historical date argument is not proof of historical coverage"}
    try:
        raw, status = fetch(url); body = json.loads(raw)
        summary = timestamp_summary((body.get("data") or {}).get("klines") or [])
        result.update(summary)
        result.update({"http_status": status, "response_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "status": "HISTORICAL_BYTES_LOCATED_NOT_ADMITTED" if summary["requested_window_rows"] else "NO_REQUESTED_WINDOW_MINUTE_ROWS"})
    except Exception as exc:
        result.update({"status": "PROBE_UNAVAILABLE_NOT_DATA_ABSENCE_PROOF", "error_type": type(exc).__name__})
    return result

def tushare_probe() -> dict:
    # Do not try example, leaked, shared, or fabricated tokens.
    token = os.environ.get("TUSHARE_TOKEN", "")
    out = {"source": "Tushare_etf_mins", "docs": DOCS["tushare"], "documented_capability": "More than ten years; 1/5/15/30/60min; at most 8000 rows per request; separate permission applies"}
    if not token:
        return {**out, "status": "NOT_ATTEMPTED_AUTH_NOT_CONFIGURED"}
    try:
        raw, status = fetch("https://api.tushare.pro", {"api_name": "etf_mins", "token": token, "params": {"ts_code": "512100.SH", "freq": "1min", "start_date": "2021-01-04 09:00:00", "end_date": "2021-01-08 16:00:00"}, "fields": "ts_code,trade_time,open,high,low,close,vol,amount"})
        body = json.loads(raw)
        if body.get("code") != 0:
            return {**out, "status": "PROVIDER_ACCESS_NOT_GRANTED", "provider_code": body.get("code"), "http_status": status}
        data = body.get("data") or {}; cols = data.get("fields") or []
        items = data.get("items") or []; k = cols.index("trade_time")
        stats = timestamp_summary([str(row[k]) for row in items])
        return {**out, **stats, "status": "HISTORICAL_SAMPLE_LOCATED_NOT_ADMITTED", "response_sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}
    except Exception as exc:
        return {**out, "status": "PROBE_UNAVAILABLE", "error_type": type(exc).__name__}

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    with ThreadPoolExecutor(max_workers=3) as pool:
        inventories = list(pool.map(repository_inventory, REPOS))
        public = list(pool.map(eastmoney_probe, ("512100", "588000")))
    receipt = {"schema_id": "factorlab_carrier_source_inventory@1.0", "observed_at_utc": datetime.now(timezone.utc).isoformat(), "requested_window": {"start": START, "end": END}, "repositories": inventories, "public_probes": public, "licensed_route": tushare_probe(), "ETF_strategy_outcomes_read": False, "raw_provider_data_committed": False, "production_authority": False, "BLACKBOX_query_count": 3}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"repository_statuses": {x["repository"]: x["status"] for x in inventories}, "public_probe_statuses": [x["status"] for x in public], "licensed_route_status": receipt["licensed_route"]["status"]}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
