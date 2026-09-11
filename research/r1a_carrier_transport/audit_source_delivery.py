"""Source-level audit for R1_A ETF delivery (public-safe receipts only).

Reads private or cloud_pack bytes plus authorized local DataHub lake partitions.
Does not impute prices, relax gates, or read strategy outcomes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

DATASET = "bars_cn_a_1m_raw_canonical_4ceca170a851"
LAKE = f".runtime/live/lake/bars/dataset_version={DATASET}/instrument_type=etf"
WINDOW = {"start": "2021-01-01", "end": "2025-12-31"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_wall_clock(values: pd.Series) -> pd.DatetimeIndex:
    text = values.astype(str)
    if text.str.endswith("Z").all():
        parsed = pd.to_datetime(text.str.removesuffix("Z"), errors="raise")
        return pd.DatetimeIndex(parsed).tz_localize("Asia/Shanghai")
    index = pd.DatetimeIndex(pd.to_datetime(text, format="mixed", errors="raise"))
    if index.tz is None:
        return index.tz_localize("Asia/Shanghai")
    return index.tz_convert("Asia/Shanghai")


def session_mask(index: pd.DatetimeIndex) -> np.ndarray:
    clock = index.hour * 60 + index.minute
    return ((clock >= 570) & (clock <= 690)) | ((clock >= 781) & (clock <= 900))


def load_lake_year(datahub: Path, symbol: str, year: int) -> pd.DataFrame:
    root = datahub / LAKE
    parts = []
    for month in range(1, 13):
        path = root / f"trading_month={year}-{month:02d}" / "data_0.parquet"
        if path.is_file():
            parts.append(pd.read_parquet(path, filters=[("symbol", "=", symbol)]))
    if not parts:
        return pd.DataFrame()
    return pd.concat(parts, ignore_index=True)


def dedup_audit(raw: pd.DataFrame) -> dict:
    if raw.empty:
        return {"raw_rows": 0}
    ts = parse_wall_clock(raw["timestamp"])
    dup_mask = ts.duplicated(keep=False)
    dup_count = int(dup_mask.sum())
    unique = int(ts.nunique())
    conflicts = 0
    samples = []
    if dup_count:
        grouped = raw.assign(_ts=ts).groupby("_ts", sort=False)
        for stamp, grp in grouped:
            if len(grp) <= 1:
                continue
            cols = ["open", "high", "low", "close", "volume"]
            same = grp[cols].nunique(dropna=False).max()
            if (same > 1).any():
                conflicts += 1
                if len(samples) < 5:
                    samples.append({"timestamp": str(stamp), "rows": int(len(grp))})
    kept = raw.assign(_ts=ts).sort_values("_ts", kind="mergesort").drop_duplicates("_ts", keep="last")
    return {
        "raw_rows": int(len(raw)),
        "unique_timestamps_before_dedup": unique,
        "duplicate_timestamp_rows": dup_count,
        "duplicate_groups": int(dup_count and ts.duplicated(keep=False).sum()) ,
        "conflicting_duplicate_groups": conflicts,
        "conflict_samples": samples,
        "rows_after_keep_last": int(len(kept)),
        "rows_removed_by_dedup": int(len(raw) - len(kept)),
    }


def coverage_audit(root: Path, carrier: str, index_symbol: str, year: int, csv_path: Path, datahub: Path | None) -> dict:
    from regime_lab.market_data import load_market_data

    index = load_market_data(index_symbol, "1m", f"{year}-01-01", f"{year}-12-31", root=root)
    index_times = pd.DatetimeIndex(index.market_time_shanghai)
    exported = pd.read_csv(csv_path, dtype={"symbol": str})
    exp_ts = parse_wall_clock(exported["timestamp"])
    exported = exported.assign(_ts=exp_ts).set_index("_ts").sort_index()
    aligned = exported.reindex(index_times)
    present = aligned["close"].notna()
    zero_vol = present & (pd.to_numeric(aligned["volume"], errors="coerce").fillna(-1) == 0)
    pos_vol = present & (pd.to_numeric(aligned["volume"], errors="coerce") > 0)
    missing = ~present
    ohlc = aligned[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    invalid_price = present & ~ohlc.gt(0).all(axis=1)
    invalid_vol = present & (pd.to_numeric(aligned["volume"], errors="coerce") < 0)
    out = {
        "year": year,
        "carrier": carrier,
        "index_symbol": index_symbol,
        "index_minutes_expected": int(len(index_times)),
        "exported_rows": int(len(exported)),
        "exported_unique_timestamps": int(exp_ts.nunique()),
        "present_on_index_clock": int(present.sum()),
        "completely_missing_on_index_clock": int(missing.sum()),
        "present_zero_volume": int(zero_vol.sum()),
        "present_positive_volume": int(pos_vol.sum()),
        "invalid_price_rows_on_index_clock": int(invalid_price.sum()),
        "invalid_volume_rows_on_index_clock": int(invalid_vol.sum()),
        "record_coverage_rate": float(present.mean()),
        "positive_volume_coverage_rate": float(pos_vol.mean()),
        "categories_mutually_exclusive_on_index_clock": True,
        "category_sum_check": int(missing.sum() + zero_vol.sum() + pos_vol.sum()),
        "csv_path": str(csv_path.relative_to(root)),
        "csv_sha256": sha256(csv_path),
    }
    if datahub is not None:
        lake_symbol = carrier.split(".")[0]
        raw = load_lake_year(datahub, lake_symbol, year)
        if not raw.empty:
            pre = raw.copy()
            ts = parse_wall_clock(pre["timestamp"])
            pre = pre.loc[session_mask(ts)]
            days = ts.strftime("%Y-%m-%d")
            pre = pre.loc[(days >= WINDOW["start"]) & (days <= WINDOW["end"])]
            out["lake_raw_rows_year"] = int(len(raw))
            out["lake_after_session_window_filter"] = int(len(pre))
            out["deduplication"] = dedup_audit(pre)
        else:
            out["lake_raw_rows_year"] = 0
            out["deduplication"] = {"status": "LAKE_PARTITION_ABSENT"}
    return out


def corporate_action_audit(datahub: Path) -> dict:
    nav_root = datahub / ".runtime/live/staging/fund_nav_full_history_20260804"
    out = {}
    for sym, carrier in [("512100", "512100.SH"), ("588000", "588000.SH")]:
        path = nav_root / f"{sym}.parquet"
        frame = pd.read_parquet(path)
        frame["nav_date"] = frame["nav_date"].astype(str)
        window = frame[(frame["nav_date"] >= WINDOW["start"]) & (frame["nav_date"] <= WINDOW["end"])]
        div = frame[frame["dividend_info"].notna() & (frame["dividend_info"].astype(str).str.strip() != "")]
        div_window = div[(div["nav_date"] >= WINDOW["start"]) & (div["nav_date"] <= WINDOW["end"])]
        before = div[div["nav_date"] < WINDOW["start"]]
        out[carrier] = {
            "source_path": str(path),
            "source_sha256": sha256(path),
            "nav_rows_in_window": int(len(window)),
            "dividend_info_rows_in_window": int(len(div_window)),
            "dividend_info_rows_before_window": int(len(before)),
            "window_events": [
                {"nav_date": str(r.nav_date), "dividend_info": str(r.dividend_info), "source_url": str(r.source_url)}
                for r in div_window.itertuples(index=False)
            ],
            "pre_window_events": [
                {"nav_date": str(r.nav_date), "dividend_info": str(r.dividend_info)}
                for r in before.itertuples(index=False)
            ],
        }
    return out


def run(root: Path, datahub: Path, pack: str, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    pack_dir = root / pack
    carriers = {}
    for carrier, index in [("512100.SH", "000852.SH"), ("588000.SH", "000688.SH")]:
        code = carrier.split(".")[0]
        years = {}
        for year in range(2021, 2026):
            csv_path = pack_dir / "prices" / f"{code}_{year}.csv"
            years[str(year)] = coverage_audit(root, carrier, index, year, csv_path, datahub)
        carriers[carrier] = years
    source_chain = {
        "timestamp_dictionary": {
            "upstream_contract": "cn_a_session_end_label_no_noon_partial_v2",
            "bar_align": "session_end_label_v2",
            "stored_form": "trading_dayTHH:MM:00Z",
            "interpretation": "Z is label encoding for Shanghai wall-clock minute-end, not UTC conversion",
            "evidence": [
                "unified_datahub/docs/modules/history/canonical-bars-whitepaper.md §5 session bucket",
                "unified_datahub/src/datahub/storage/query/session_offset_contract.py BAR_ALIGN_OFFICIAL",
                "factor_lab csi1000 export uses str.removesuffix('Z') then tz_localize('Asia/Shanghai')",
            ],
            "utc_conversion_would_mismatch_index": "UNKNOWN_not_measured_here",
        },
        "dataset_version": DATASET,
        "lake_partition": LAKE,
    }
    corp = corporate_action_audit(datahub)
    primary = carriers["512100.SH"]["2021"]
    conclusion = {
        "question": "Is 94.478738% caused by true zero-volume or export defect?",
        "answer": (
            "TRUE_ZERO_VOLUME_ON_INDEX_CLOCK"
            if primary["completely_missing_on_index_clock"] == 0 and primary["present_zero_volume"] > 0
            else "UNKNOWN_OR_MIXED"
        ),
        "evidence": {
            "missing_timestamps": primary["completely_missing_on_index_clock"],
            "zero_volume_timestamps": primary["present_zero_volume"],
            "positive_volume_timestamps": primary["present_positive_volume"],
            "positive_volume_coverage_rate": primary["positive_volume_coverage_rate"],
        },
        "unknowns": [
            "Whether each zero-volume minute had no exchange print vs vendor placeholder — not independently exchange-verified",
        ],
    }
    receipt = {
        "schema_id": "factorlab_r1a_source_delivery_audit@1.0",
        "pack": pack,
        "window": WINDOW,
        "carriers": carriers,
        "source_chain": source_chain,
        "corporate_actions": corp,
        "primary_512100_2021_conclusion": conclusion,
        "coverage_gate_unchanged": 0.95,
    }
    (output / "source_delivery_audit.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        "# R1_A ETF source delivery audit",
        "",
        f"Pack: `{pack}`",
        "",
        "## 512100.SH 2021 attribution",
        "",
        f"- Index minutes expected: {primary['index_minutes_expected']}",
        f"- Present on index clock: {primary['present_on_index_clock']}",
        f"- Completely missing: {primary['completely_missing_on_index_clock']}",
        f"- Present zero volume: {primary['present_zero_volume']}",
        f"- Present positive volume: {primary['present_positive_volume']}",
        f"- Record coverage: {primary['record_coverage_rate']:.6%}",
        f"- Positive-volume coverage: {primary['positive_volume_coverage_rate']:.6%}",
        f"- Conclusion: **{conclusion['answer']}**",
        "",
        "Categories on the index clock are mutually exclusive: missing | zero-volume | positive-volume.",
        "",
        "## Timestamp chain",
        "",
        "Upstream stores `trading_dayTHH:MM:00Z` under session_end_label_v2; export strips `Z` and localizes Asia/Shanghai (not UTC convert).",
        "",
        f"## Deduplication 512100 2021",
        "",
        json.dumps(primary.get("deduplication", {}), ensure_ascii=False, indent=2),
    ]
    (output / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--datahub-root", type=Path, required=True)
    parser.add_argument("--pack", default="data/r1a_carrier_prices/cloud_pack_v1")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    receipt = run(args.root.resolve(), args.datahub_root.resolve(), args.pack, args.output)
    print(json.dumps(receipt["primary_512100_2021_conclusion"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
