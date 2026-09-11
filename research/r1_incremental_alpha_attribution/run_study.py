#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from regime_lab.market_data import load_market_data
from research.r1_incremental_alpha_attribution.core import (
    HORIZONS,
    SEGMENTS,
    build_r1_events_and_controls,
    match_events,
    paired_outcomes,
    path_attribution,
    summarize_incremental,
    summarize_path,
)

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "docs/governance/R1_INCREMENTAL_ALPHA_ATTRIBUTION_FREEZE@1.0.json"
PRICE_FREEZE = ROOT / "docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json"
EVIDENCE_DIR = ROOT / "docs/ops/evidence/r1_incremental_alpha_20260911"
RECEIPT = EVIDENCE_DIR / "attribution_receipt.json"
MATCH_LEDGER = EVIDENCE_DIR / "matched_pairs.csv"
OUTCOME_LEDGER = EVIDENCE_DIR / "paired_outcomes.csv"
PATH_LEDGER = EVIDENCE_DIR / "path_attribution.csv"
REPORT = ROOT / "docs/research/R1_INCREMENTAL_ALPHA_ATTRIBUTION_20260911.md"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return None


def load_symbol(symbol: str, start: str, end: str) -> pd.DataFrame:
    frame = load_market_data(symbol, "1m", start, end, root=ROOT)
    if frame.empty:
        raise RuntimeError(f"no data for {symbol}")
    frame = frame.copy()
    frame["trading_day"] = frame["trading_day"].astype(str)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    if frame["close"].isna().any() or (frame["close"] <= 0).any():
        raise RuntimeError(f"invalid close data for {symbol}")
    return frame.sort_values("market_time_shanghai", kind="stable").reset_index(drop=True)


def bp(x: float | None) -> str:
    return "NA" if x is None else f"{x * 10000:+.2f}"


def bp_raw(x: float | None) -> str:
    return "NA" if x is None else f"{x:+.2f}"


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{x * 100:.1f}%"


def render_incremental_table(symbol: str, summary: dict[str, Any]) -> str:
    name = "CSI1000 / 000852.SH" if symbol == "000852.SH" else "STAR50 / 000688.SH"
    lines = [
        f"### {name}",
        "",
        "| Cell | h | matched/eligible | event mean bp | control mean bp | incremental mean bp | incremental median bp | pair+ | bootstrap 95% bp | +years | LONG inc bp | SHORT inc bp | strong |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cell in ("R1_A", "R1_B"):
        for h in HORIZONS:
            info = summary[cell][str(h)]
            m = info["matching"]
            ci = info["bootstrap_95pct_mean_ci"]
            long = info["incremental_by_side"]["LONG"]
            short = info["incremental_by_side"]["SHORT"]
            lines.append(
                f"| {cell} | {h} | {m['matched_events']}/{m['eligible_events']} | {bp(info['event']['mean'])} | {bp(info['control']['mean'])} | "
                f"{bp(info['incremental']['mean'])} | {bp(info['incremental']['median'])} | {pct(info['incremental']['positive_fraction'])} | "
                f"[{bp(ci[0])}, {bp(ci[1])}] | {info['positive_annual_incremental_mean_years']}/5 | {bp(long['mean'])} | {bp(short['mean'])} | "
                f"{'YES' if info['strong_incremental_support'] else 'no'} |"
            )
    return "\n".join(lines)


def render_match_quality(symbol: str, meta: dict[str, Any]) -> str:
    name = "CSI1000" if symbol == "000852.SH" else "STAR50"
    lines = [
        f"### {name} matching quality",
        "",
        "| Cell | eligible | matched | coverage | unique controls | median distance | p90 distance |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in ("R1_A", "R1_B"):
        x = meta[cell]
        lines.append(
            f"| {cell} | {x['eligible_events']} | {x['matched_events']} | {pct(x['coverage'])} | {x['unique_controls']} | "
            f"{x['median_match_distance']:.3f} | {x['p90_match_distance']:.3f} |"
        )
    return "\n".join(lines)


def render_path_table(symbol: str, path_summary: dict[str, Any]) -> str:
    name = "CSI1000 / 000852.SH" if symbol == "000852.SH" else "STAR50 / 000688.SH"
    lines = [f"### {name} additive signed-log path attribution", ""]
    for cell in ("R1_A", "R1_B"):
        x = path_summary[cell]
        lines += [
            f"#### {cell}",
            "",
            "| Segment | event mean bp | control mean bp | incremental mean bp |",
            "|---|---:|---:|---:|",
        ]
        for a, b in SEGMENTS:
            s = x["segments"][f"seg_{a}_{b}"]
            lines.append(f"| {a}→{b} bars | {bp_raw(s['event_mean_bp'])} | {bp_raw(s['control_mean_bp'])} | {bp_raw(s['incremental_mean_bp'])} |")
        lines += [
            "",
            "240-bar session decomposition:",
            "",
            "| Component | event mean bp | control mean bp | incremental mean bp |",
            "|---|---:|---:|---:|",
        ]
        for component in ("same_session", "overnight", "next_session"):
            s = x["h240_session_decomposition"][component]
            lines.append(f"| {component} | {bp_raw(s['event_mean_bp'])} | {bp_raw(s['control_mean_bp'])} | {bp_raw(s['incremental_mean_bp'])} |")
        e = x["extrema_timing"]
        lines += [
            "",
            f"Event median bars-to-MFE / MAE: **{e['event_median_bars_to_MFE']:.1f} / {e['event_median_bars_to_MAE']:.1f}**. "
            f"MFE realized by 30/60/120 bars: **{pct(e['event_fraction_MFE_by_30'])} / {pct(e['event_fraction_MFE_by_60'])} / {pct(e['event_fraction_MFE_by_120'])}**.",
            "",
        ]
    return "\n".join(lines)


def common_strong(summary: dict[str, Any]) -> dict[str, list[int]]:
    out = {"R1_A": [], "R1_B": []}
    for cell in out:
        for h in HORIZONS:
            if summary["000852.SH"][cell][str(h)]["strong_incremental_support"] and summary["000688.SH"][cell][str(h)]["strong_incremental_support"]:
                out[cell].append(int(h))
    return out


def render_report(receipt: dict[str, Any]) -> str:
    common = receipt["common_strong_incremental_horizons"]
    lines = [
        "# R1 matched-parent incremental-alpha attribution — 2026-09-11",
        "",
        "Status: **COMPLETE / ATTRIBUTION ONLY / NO HORIZON SELECTED / NO INSTRUMENT MAPPING**",
        "",
        "This study asks whether R1 adds return beyond generic continuation of an otherwise similar intact parent trend. Each R1 event is paired to a results-blind matched parent-state clock with the same year, parent direction and 30-minute clock bucket, then nearest-neighbor matched on causal parent drift, path efficiency, parent age and local volatility.",
        "",
        "## Frozen boundary",
        "",
        f"Freeze: `{receipt['freeze_path']}`  ",
        f"Freeze SHA256: `{receipt['freeze_sha256']}`  ",
        f"Code commit at run: `{receipt['code_commit']}`",
        "",
        "No return, MFE/MAE, option, ETF, futures, cost, probability, year/side filter or horizon winner is used to create the controls. Control matching is with replacement and never relaxes the exact stratum after results are known.",
        "",
        "## Matching quality",
        "",
        render_match_quality("000852.SH", receipt["match_meta"]["000852.SH"]),
        "",
        render_match_quality("000688.SH", receipt["match_meta"]["000688.SH"]),
        "",
        "## Incremental return results",
        "",
        render_incremental_table("000852.SH", receipt["incremental_summary"]["000852.SH"]),
        "",
        render_incremental_table("000688.SH", receipt["incremental_summary"]["000688.SH"]),
        "",
        "A `strong` flag is horizon-local only. It requires >=80% match coverage, positive pooled paired mean, a positive event-day-cluster-bootstrap 95% lower bound, positive annual incremental mean in >=4/5 years, and positive LONG and SHORT incremental means when both sides have >=30 events. It does **not** authorize choosing that horizon.",
        "",
        f"Common strong incremental horizons across both indices: `{common}`",
        "",
        "## Price-path attribution",
        "",
        render_path_table("000852.SH", receipt["path_summary"]["000852.SH"]),
        "",
        render_path_table("000688.SH", receipt["path_summary"]["000688.SH"]),
        "",
        "## Interpretation contract",
        "",
        "If R1 remains positive relative to matched parent-state controls, the evidence supports a pullback-specific incremental alpha rather than merely generic parent-trend continuation. If the raw event return stays positive but paired incremental return does not, the prior price edge should instead be interpreted mainly as trend continuation.",
        "",
        "This study still does not choose an ETF, futures contract, option structure or executable holding period. `BLACKBOX_query_count=3`; no query #4; `production_authority=false`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    price_freeze = json.loads(PRICE_FREEZE.read_text(encoding="utf-8"))
    if freeze["status"] != "FROZEN_BEFORE_MATCHED_CONTROL_OUTCOMES":
        raise RuntimeError("attribution freeze drifted")
    if freeze["scope"]["BLACKBOX_query_4_authorized"] or freeze["scope"]["production_authority"]:
        raise RuntimeError("governance drifted")
    if freeze["scope"]["horizons_observed_bars"] != list(HORIZONS):
        raise RuntimeError("horizon drifted")
    thresholds = {k: float(v) for k, v in price_freeze["directional_change_thresholds"].items()}
    vol_ref = float(price_freeze["r1_vol_reference"])

    all_matches = []
    all_outcomes = []
    all_paths = []
    match_meta: dict[str, dict] = {}
    incremental_summary: dict[str, Any] = {}
    path_summary: dict[str, Any] = {}

    for symbol, start in (("000852.SH", "2015-01-05"), ("000688.SH", "2020-07-23")):
        frame = load_symbol(symbol, start, "2025-12-31")
        prices = frame["close"].to_numpy(float)
        days = frame["trading_day"].to_numpy(str)
        events, controls = build_r1_events_and_controls(
            prices,
            days,
            frame["market_time_shanghai"],
            thresholds,
            vol_ref,
            "2021-01-01",
            "2025-12-31",
            240,
        )
        symbol_matches = []
        symbol_meta: dict[str, Any] = {}
        for cell in ("R1_A", "R1_B"):
            matched, meta = match_events(events.loc[events["cell"].eq(cell)], controls.loc[controls["cell"].eq(cell)])
            symbol_meta[cell] = meta
            symbol_matches.append(matched)
        matches = pd.concat(symbol_matches, ignore_index=True)
        matches.insert(0, "symbol", symbol)
        outcomes = paired_outcomes(matches, prices, HORIZONS)
        outcomes.insert(0, "symbol", symbol)
        paths = path_attribution(matches, prices, days)
        paths.insert(0, "symbol", symbol)

        match_meta[symbol] = symbol_meta
        incremental_summary[symbol] = summarize_incremental(outcomes, symbol_meta)
        path_summary[symbol] = summarize_path(paths)
        all_matches.append(matches)
        all_outcomes.append(outcomes)
        all_paths.append(paths)
        print(
            f"{symbol}: events={events.groupby('cell').size().to_dict()} controls={controls.groupby('cell').size().to_dict()} "
            f"matched={matches.groupby('cell').size().to_dict()}",
            flush=True,
        )

    matches_ledger = pd.concat(all_matches, ignore_index=True)
    outcomes_ledger = pd.concat(all_outcomes, ignore_index=True)
    paths_ledger = pd.concat(all_paths, ignore_index=True)
    summary_bundle = incremental_summary
    receipt = {
        "schema_id": "factorlab_R1_incremental_alpha_attribution_receipt@1.0",
        "decision": "R1_INCREMENTAL_ATTRIBUTION_COMPLETE_NO_HORIZON_SELECTED",
        "freeze_path": str(FREEZE.relative_to(ROOT)),
        "freeze_sha256": sha256_file(FREEZE),
        "prior_price_freeze_path": str(PRICE_FREEZE.relative_to(ROOT)),
        "code_commit": git_head(),
        "match_meta": match_meta,
        "incremental_summary": incremental_summary,
        "path_summary": path_summary,
        "common_strong_incremental_horizons": common_strong(summary_bundle),
        "matching_outcome_information_used": False,
        "horizon_selected": False,
        "instrument_mapping_performed": False,
        "blackbox_query_count": 3,
        "blackbox_query_4_authorized": False,
        "production_authority": False,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    matches_ledger.to_csv(MATCH_LEDGER, index=False)
    outcomes_ledger.to_csv(OUTCOME_LEDGER, index=False)
    paths_ledger.to_csv(PATH_LEDGER, index=False)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(receipt), encoding="utf-8")
    print(json.dumps({"decision": receipt["decision"], "common_strong": receipt["common_strong_incremental_horizons"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
