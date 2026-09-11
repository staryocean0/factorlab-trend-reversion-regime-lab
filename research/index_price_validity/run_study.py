#!/usr/bin/env python3
"""Run the frozen pure cash-index price-validity study.

No option/ETF/futures data are read. No cost, threshold, horizon, side, year, or
regime selection is performed. Every frozen horizon is reported.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import pandas as pd

from regime_lab.market_data import load_market_data
from research.index_price_validity.core import evaluate_events, generate_events, summarize_window

ROOT = Path(__file__).resolve().parents[2]
FREEZE = ROOT / "docs/governance/INDEX_PRICE_VALIDITY_FREEZE@1.0.json"
EVIDENCE_DIR = ROOT / "docs/ops/evidence/index_price_validity_20260911"
RECEIPT = EVIDENCE_DIR / "price_validity_receipt.json"
LEDGER = EVIDENCE_DIR / "price_response_ledger.csv"
REPORT = ROOT / "docs/research/INDEX_PRICE_VALIDITY_STUDY_20260911.md"
HORIZONS = [1, 5, 15, 30, 60, 120, 240]


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
    required = {"trading_day", "close", "market_time_shanghai"}
    missing = required - set(frame.columns)
    if missing:
        raise RuntimeError(f"{symbol} missing columns {sorted(missing)}")
    frame = frame.copy()
    frame["trading_day"] = frame["trading_day"].astype(str)
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    if frame["close"].isna().any() or (frame["close"] <= 0).any():
        raise RuntimeError(f"invalid close data for {symbol}")
    return frame.sort_values("market_time_shanghai", kind="stable").reset_index(drop=True)


def primary_summary(ledger: pd.DataFrame, symbol: str) -> dict[str, Any]:
    block = ledger.loc[ledger["symbol"].eq(symbol)].copy()
    if symbol == "000852.SH":
        primary = block.loc[(block["entry_day"] >= "2021-01-01") & (block["entry_day"] <= "2025-12-31")]
        context = block.loc[block["entry_day"] <= "2020-12-31"]
        return {
            "primary_label": "VALIDATION_2021_2025",
            "primary": summarize_window(primary, ["2021", "2022", "2023", "2024", "2025"]),
            "context_label": "DEV_2015_2020",
            "context": summarize_window(context, ["2016", "2017", "2018", "2019", "2020"]),
        }
    primary = block.loc[(block["entry_day"] >= "2021-01-01") & (block["entry_day"] <= "2025-12-31")]
    context = block.loc[block["entry_day"].str.startswith("2020")]
    return {
        "primary_label": "TRANSPORT_2021_2025",
        "primary": summarize_window(primary, ["2021", "2022", "2023", "2024", "2025"]),
        "context_label": "CONTEXT_2020",
        "context": summarize_window(context, ["2020"]),
    }


def robust_cells(summary: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cell, horizons in summary.items():
        for horizon, info in horizons.items():
            if info["robust_price_edge"]:
                rows.append(
                    {
                        "cell": cell,
                        "horizon": int(horizon),
                        "mean": info["pooled"]["mean"],
                        "median": info["pooled"]["median"],
                        "win_rate": info["pooled"]["win_rate"],
                        "positive_annual_mean_years": info["positive_annual_mean_years"],
                    }
                )
    return rows


def sign_matrix(summaries: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for cell in ("R1_A", "R1_B", "R2_A", "R2_B"):
        for h in HORIZONS:
            hkey = str(h)
            csi = summaries["000852.SH"]["primary"][cell][hkey]
            star = summaries["000688.SH"]["primary"][cell][hkey]
            rows.append(
                {
                    "cell": cell,
                    "horizon": h,
                    "CSI1000_mean_positive": bool(csi["pooled"]["mean"] is not None and csi["pooled"]["mean"] > 0),
                    "CSI1000_median_positive": bool(csi["pooled"]["median"] is not None and csi["pooled"]["median"] > 0),
                    "STAR50_mean_positive": bool(star["pooled"]["mean"] is not None and star["pooled"]["mean"] > 0),
                    "STAR50_median_positive": bool(star["pooled"]["median"] is not None and star["pooled"]["median"] > 0),
                    "both_mean_positive": bool(
                        csi["pooled"]["mean"] is not None
                        and star["pooled"]["mean"] is not None
                        and csi["pooled"]["mean"] > 0
                        and star["pooled"]["mean"] > 0
                    ),
                }
            )
    return rows


def bp(value: float | None) -> str:
    return "NA" if value is None else f"{value * 10000:+.2f}"


def pct(value: float | None) -> str:
    return "NA" if value is None else f"{value * 100:.1f}%"


def render_primary_table(symbol: str, label: str, summary: dict[str, Any]) -> str:
    name = "CSI1000 / 000852.SH" if symbol == "000852.SH" else "STAR50 / 000688.SH"
    lines = [
        f"### {name} — {label}",
        "",
        "| Cell | h | n | mean bp | median bp | win | mean MFE bp | mean MAE bp | +years | LONG mean bp | SHORT mean bp | robust |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for cell in ("R1_A", "R1_B", "R2_A", "R2_B"):
        for h in HORIZONS:
            info = summary[cell][str(h)]
            pooled = info["pooled"]
            long = info["by_side"]["LONG"]
            short = info["by_side"]["SHORT"]
            lines.append(
                f"| {cell} | {h} | {pooled['n']} | {bp(pooled['mean'])} | {bp(pooled['median'])} | {pct(pooled['win_rate'])} | "
                f"{bp(pooled['mean_MFE'])} | {bp(pooled['mean_MAE'])} | {info['positive_annual_mean_years']}/5 | "
                f"{bp(long['mean'])} | {bp(short['mean'])} | {'YES' if info['robust_price_edge'] else 'no'} |"
            )
    return "\n".join(lines)


def render_report(receipt: dict[str, Any]) -> str:
    summaries = receipt["summaries"]
    csi = summaries["000852.SH"]
    star = summaries["000688.SH"]
    cross = receipt["cross_index_sign_matrix"]
    both_positive = [f"{x['cell']}@{x['horizon']}" for x in cross if x["both_mean_positive"]]
    lines = [
        "# Pure index price-validity study — 2026-09-11",
        "",
        "Status: **COMPLETE / PRICE-LAYER DIAGNOSTIC ONLY / NO INSTRUMENT IMPLEMENTATION**",
        "",
        "This study fills the missing layer between certified R1/R2 mechanisms and instrument implementation. It asks only whether the causal signal direction is followed by favorable cash-index price movement. Synthetic SHORT returns are allowed for research even though the cash index itself is not shortable.",
        "",
        "## Frozen design",
        "",
        "- entry: next observed 1m close after causal event confirmation;",
        "- primary outcome: zero-cost signed gross cash-index return;",
        "- horizons: 1, 5, 15, 30, 60, 120, 240 observed 1m bars;",
        "- report every horizon; no winner selection;",
        "- LONG and SHORT sides reported separately;",
        "- MFE/MAE reported on the same frozen horizons;",
        "- CSI1000 primary reusable window: 2021–2025;",
        "- STAR50 2021–2025 is a cross-index transport check, not a new mechanism certification;",
        "- no cost, option, ETF, futures, probability threshold, sizing, stop, target, regime, time-of-day, or BLACKBOX search.",
        "",
        f"Freeze: `{receipt['freeze_path']}`  ",
        f"Freeze SHA256: `{receipt['freeze_sha256']}`  ",
        f"Code commit at run: `{receipt['code_commit']}`",
        "",
        "## Primary results",
        "",
        render_primary_table("000852.SH", csi["primary_label"], csi["primary"]),
        "",
        render_primary_table("000688.SH", star["primary_label"], star["primary"]),
        "",
        "## Robust-edge flags",
        "",
        "A `robust` flag is horizon-local only: positive pooled mean, positive pooled median, win rate >50%, positive annual mean in at least 4/5 years, and positive mean on both LONG and SHORT sides when each side has at least 30 events. It is **not** permission to select that horizon for trading.",
        "",
        f"- CSI1000 robust cells/horizons: `{receipt['robust_edges']['000852.SH']}`",
        f"- STAR50 transport robust cells/horizons: `{receipt['robust_edges']['000688.SH']}`",
        f"- horizons/cells with positive pooled mean on both indices: `{both_positive}`",
        "",
        "## Interpretation boundary",
        "",
        "This result answers a narrower question than the earlier economic translations. A positive price edge means the signal contains directional information in the index path. It does not by itself prove ETF/futures/options executability after spreads, fees, T+1, borrow, basis, margin, or inventory constraints.",
        "",
        "The earlier option failures remain valid instrument-mapping failures, but they do not override this price-layer evidence.",
        "",
        "`BLACKBOX_query_count=3`; no query #4; `production_authority=false`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if freeze["status"] != "FROZEN_BEFORE_NEW_PRICE_LAYER_RUN":
        raise RuntimeError("price-validity freeze status drifted")
    if freeze["blackbox_query_4_authorized"] is True or freeze["production_authority"] is True:
        raise RuntimeError("governance boundary drifted")
    thresholds = {k: float(v) for k, v in freeze["directional_change_thresholds"].items()}
    vol_ref = float(freeze["r1_vol_reference"])

    all_ledgers = []
    event_inventory: dict[str, Any] = {}
    for symbol, start, end in (
        ("000852.SH", "2015-01-05", "2025-12-31"),
        ("000688.SH", "2020-07-23", "2025-12-31"),
    ):
        frame = load_symbol(symbol, start, end)
        prices = frame["close"].to_numpy(float)
        days = frame["trading_day"].to_numpy(str)
        events = generate_events(prices, days, thresholds, vol_ref)
        event_inventory[symbol] = {
            cell: int((events["cell"] == cell).sum()) for cell in ("R1_A", "R1_B", "R2_A", "R2_B")
        }
        ledger = evaluate_events(events, prices, days, HORIZONS, symbol)
        all_ledgers.append(ledger)
        print(f"{symbol}: rows={len(frame)} events={event_inventory[symbol]} price_response_rows={len(ledger)}", flush=True)

    ledger = pd.concat(all_ledgers, ignore_index=True)
    summaries = {symbol: primary_summary(ledger, symbol) for symbol in ("000852.SH", "000688.SH")}
    receipt = {
        "schema_id": "factorlab_index_price_validity_receipt@1.0",
        "decision": "PRICE_LAYER_VALIDITY_COMPLETED_NO_HORIZON_SELECTED",
        "freeze_path": str(FREEZE.relative_to(ROOT)),
        "freeze_sha256": sha256_file(FREEZE),
        "code_commit": git_head(),
        "event_inventory": event_inventory,
        "summaries": summaries,
        "robust_edges": {
            "000852.SH": robust_cells(summaries["000852.SH"]["primary"]),
            "000688.SH": robust_cells(summaries["000688.SH"]["primary"]),
        },
        "cross_index_sign_matrix": sign_matrix(summaries),
        "primary_cost_bps": 0.0,
        "horizon_selected": False,
        "etf_tested": False,
        "option_outcomes_read": False,
        "blackbox_query_count": 3,
        "blackbox_query_4_authorized": False,
        "production_authority": False,
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(LEDGER, index=False)
    RECEIPT.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(render_report(receipt), encoding="utf-8")
    print(json.dumps({"decision": receipt["decision"], "robust_edges": receipt["robust_edges"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
