#!/usr/bin/env python3
"""Run the single frozen R5-B1 TRAIN/VALIDATION limited diagnostic.

The R5 state/B0/B1 construction is imported from the exact historical frozen
runner. This file adds only the two diagnostics preregistered in
`docs/research/R5_B1_LIMITED_DIAGNOSTIC_PROTOCOL_20260910.md`.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

EXPECTED_OLD_DATA_SHA256 = "bea21fa9dd9532e21605511e07561b33d5569f86f69f5a487507531593b14c48"
EXPECTED_OLD_ROWS = 70114
EXPECTED_FROZEN_COMMIT = "cf8397c12a9defa243dc272224dedebe6ccd3251"
EXPECTED_RUNNER_BLOB = "cd0ac94f7f8dc4fba7c9ee25701bcca02f551f2a"
REQUIRED = ["symbol", "trading_day", "close", "bar_end_shanghai"]
YEARS = range(2015, 2021)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_frozen_module(path: Path):
    spec = importlib.util.spec_from_file_location("frozen_r5", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import frozen R5 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_native(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in REQUIRED if c not in frame.columns]
    if missing:
        raise RuntimeError(f"missing required columns: {missing}")
    out = frame[REQUIRED].copy()
    out["symbol"] = out["symbol"].astype(str)
    out["trading_day"] = out["trading_day"].astype(str)
    out["close"] = pd.to_numeric(out["close"], errors="raise").astype(float)
    out["bar_end_shanghai"] = pd.to_datetime(out["bar_end_shanghai"], errors="raise")
    out = out.sort_values("bar_end_shanghai", kind="stable").reset_index(drop=True)
    return out


def current_partition_native(current_root: Path) -> pd.DataFrame:
    parts = []
    for year in YEARS:
        path = current_root / f"{year}.parquet"
        if not path.exists():
            raise RuntimeError(f"missing current partition: {path}")
        parts.append(pd.read_parquet(path, columns=REQUIRED))
    return normalize_native(pd.concat(parts, ignore_index=True))


def compare_native(old: pd.DataFrame, current: pd.DataFrame) -> dict[str, Any]:
    old_n = normalize_native(old)
    cur_n = normalize_native(current)
    result: dict[str, Any] = {
        "old_rows": int(len(old_n)),
        "current_rows": int(len(cur_n)),
        "expected_old_rows": EXPECTED_OLD_ROWS,
        "symbol_equal": False,
        "trading_day_equal": False,
        "timestamp_equal": False,
        "close_exact_equal": False,
        "equivalent": False,
    }
    if len(old_n) != len(cur_n) or len(old_n) != EXPECTED_OLD_ROWS:
        return result
    result["symbol_equal"] = bool(np.array_equal(old_n["symbol"].to_numpy(), cur_n["symbol"].to_numpy()))
    result["trading_day_equal"] = bool(np.array_equal(old_n["trading_day"].to_numpy(), cur_n["trading_day"].to_numpy()))
    result["timestamp_equal"] = bool(np.array_equal(old_n["bar_end_shanghai"].astype("int64").to_numpy(), cur_n["bar_end_shanghai"].astype("int64").to_numpy()))
    result["close_exact_equal"] = bool(np.array_equal(old_n["close"].to_numpy(dtype=float), cur_n["close"].to_numpy(dtype=float)))
    result["equivalent"] = bool(all(result[k] for k in ("symbol_equal", "trading_day_equal", "timestamp_equal", "close_exact_equal")))
    if not result["equivalent"]:
        mismatch = np.zeros(len(old_n), dtype=bool)
        mismatch |= old_n["symbol"].to_numpy() != cur_n["symbol"].to_numpy()
        mismatch |= old_n["trading_day"].to_numpy() != cur_n["trading_day"].to_numpy()
        mismatch |= old_n["bar_end_shanghai"].astype("int64").to_numpy() != cur_n["bar_end_shanghai"].astype("int64").to_numpy()
        mismatch |= old_n["close"].to_numpy(dtype=float) != cur_n["close"].to_numpy(dtype=float)
        result["mismatch_rows"] = int(mismatch.sum())
        first = np.flatnonzero(mismatch)
        if len(first):
            result["first_mismatch_index"] = int(first[0])
    return result


def eligible_B_frame(r5, state: pd.DataFrame) -> pd.DataFrame:
    frame = state.copy()
    frame["next_z"] = frame["z"].shift(-1)
    same_next_segment = frame["segment_id"].eq(frame["segment_id"].shift(-1))
    valid = frame["state_available"] & frame["z"].notna() & frame["next_z"].notna() & same_next_segment
    return frame.loc[valid].copy()


def fit_slope(frame: pd.DataFrame) -> dict[str, Any]:
    if len(frame) < 20:
        return {"n": int(len(frame)), "intercept": None, "slope": None}
    z = frame["z"].to_numpy(dtype=float)
    y = frame["next_z"].to_numpy(dtype=float)
    if not np.isfinite(z).all() or not np.isfinite(y).all() or float(np.std(z)) == 0.0:
        return {"n": int(len(frame)), "intercept": None, "slope": None}
    X = np.column_stack([np.ones(len(frame)), z])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {"n": int(len(frame)), "intercept": float(beta[0]), "slope": float(beta[1])}


def daily_breadth(r5, train: pd.DataFrame, val: pd.DataFrame) -> dict[str, Any]:
    fitted = {}
    predictions = {}
    y_val = val["next_z"].to_numpy(dtype=float)
    for candidate in ("B0", "B1"):
        X_train, y_train = r5._design_B(train, candidate)
        beta = r5._fit_ols(X_train, y_train)
        X_val, _ = r5._design_B(val, candidate)
        fitted[candidate] = beta
        predictions[candidate] = r5._predict(X_val, beta)

    gain = (y_val - predictions["B0"]) ** 2 - (y_val - predictions["B1"]) ** 2
    temp = val[["trading_day", "year"]].copy()
    temp["gain"] = gain
    by_day = temp.groupby(["trading_day", "year"], sort=True, as_index=False)["gain"].sum()
    positive = by_day.loc[by_day["gain"] > 0.0, "gain"].sort_values(ascending=False)
    if len(positive):
        top_n = max(1, int(math.ceil(0.10 * len(positive))))
        concentration = float(positive.iloc[:top_n].sum() / positive.sum()) if float(positive.sum()) > 0 else None
    else:
        top_n = 0
        concentration = None

    q = by_day["gain"].quantile([0.10, 0.25, 0.50, 0.75, 0.90]).to_dict()
    yearly = {str(year): float(by_day.loc[by_day["year"] == year, "gain"].sum()) for year in (2019, 2020)}
    pooled = float(by_day["gain"].sum())
    positive_fraction = float((by_day["gain"] > 0.0).mean())
    supported = bool(
        pooled > 0.0
        and yearly["2019"] > 0.0
        and yearly["2020"] > 0.0
        and positive_fraction >= 0.50
        and concentration is not None
        and concentration <= 0.50
    )
    return {
        "TRAIN_coefficients": {k: [float(x) for x in v] for k, v in fitted.items()},
        "validation_days": int(len(by_day)),
        "positive_days": int((by_day["gain"] > 0.0).sum()),
        "zero_days": int((by_day["gain"] == 0.0).sum()),
        "negative_days": int((by_day["gain"] < 0.0).sum()),
        "positive_day_fraction": positive_fraction,
        "pooled_total_SSE_gain": pooled,
        "year_total_SSE_gain": yearly,
        "positive_gain_top10pct_day_count": top_n,
        "positive_gain_top10pct_concentration": concentration,
        "day_gain_quantiles": {str(k): float(v) for k, v in q.items()},
        "supported": supported,
    }


def monotonic_shape(train: pd.DataFrame, val: pd.DataFrame) -> dict[str, Any]:
    anti_train = train["anti_persistence"].to_numpy(dtype=float)
    internal = np.quantile(anti_train, [0.20, 0.40, 0.60, 0.80])
    if len(np.unique(internal)) != 4:
        return {"status": "non_unique_train_quintile_edges", "supported": False}
    edges = np.concatenate(([-np.inf], internal, [np.inf]))
    val_work = val.copy()
    val_work["anti_bin"] = np.searchsorted(internal, val_work["anti_persistence"].to_numpy(dtype=float), side="right")
    train_work = train.copy()
    train_work["anti_bin"] = np.searchsorted(internal, train_work["anti_persistence"].to_numpy(dtype=float), side="right")

    bins = []
    slopes = []
    medians = []
    for idx in range(5):
        v = val_work.loc[val_work["anti_bin"] == idx]
        t = train_work.loc[train_work["anti_bin"] == idx]
        pooled = fit_slope(v)
        slopes.append(pooled["slope"])
        median_anti = float(v["anti_persistence"].median()) if len(v) else None
        medians.append(median_anti)
        bins.append({
            "quintile": idx + 1,
            "edge_low": None if not np.isfinite(edges[idx]) else float(edges[idx]),
            "edge_high": None if not np.isfinite(edges[idx + 1]) else float(edges[idx + 1]),
            "TRAIN_n": int(len(t)),
            "VALIDATION_n": int(len(v)),
            "VALIDATION_median_anti_persistence": median_anti,
            "VALIDATION_pooled": pooled,
            "VALIDATION_2019": fit_slope(v.loc[v["year"] == 2019]),
            "VALIDATION_2020": fit_slope(v.loc[v["year"] == 2020]),
        })

    if any(x is None for x in slopes) or any(x is None for x in medians):
        return {"status": "insufficient_bin_slope", "bins": bins, "supported": False}
    s = np.asarray(slopes, dtype=float)
    m = np.asarray(medians, dtype=float)
    adjacent_nonincreasing = int(np.sum(np.diff(s) <= 0.0))
    rank_m = pd.Series(m).rank(method="average").to_numpy(dtype=float)
    rank_s = pd.Series(s).rank(method="average").to_numpy(dtype=float)
    spearman = float(np.corrcoef(rank_m, rank_s)[0, 1])
    strongest_more_negative = bool(s[-1] < s[0])
    supported = bool(strongest_more_negative and adjacent_nonincreasing >= 3 and spearman <= -0.80)
    return {
        "status": "evaluated",
        "TRAIN_internal_quintile_edges": [float(x) for x in internal],
        "bins": bins,
        "adjacent_nonincreasing_steps": adjacent_nonincreasing,
        "strongest_more_negative_than_weakest": strongest_more_negative,
        "spearman_anti_vs_slope": spearman,
        "supported": supported,
    }


def run(current_root: Path, frozen_root: Path) -> dict[str, Any]:
    old_data_path = frozen_root / "data/development/5m_offset_0.parquet"
    frozen_runner_path = frozen_root / "scripts/run_broad_rmr_R5_multiscale_serial_dependence.py"
    if sha256_file(old_data_path) != EXPECTED_OLD_DATA_SHA256:
        raise RuntimeError("frozen data SHA256 mismatch")

    r5 = load_frozen_module(frozen_runner_path)
    old_native = r5.load_native(old_data_path)
    current_native = current_partition_native(current_root)
    identity = compare_native(old_native[REQUIRED], current_native)
    if not identity["equivalent"]:
        raise RuntimeError("current repository 2015-2020 data are not row-for-row equivalent to frozen R5 source")

    returns = r5.build_continuous_returns(old_native)
    normalized = r5.add_causal_normalization(returns)
    state = r5.add_memory_state(normalized)
    frame = eligible_B_frame(r5, state)
    train = frame.loc[frame["role"] == "TRAIN"].copy()
    val = frame.loc[frame["role"] == "VALIDATION"].copy()

    breadth = daily_breadth(r5, train, val)
    shape = monotonic_shape(train, val)
    survives = bool(breadth["supported"] and shape["supported"])
    adjudication = (
        "R5_B1_limited_diagnostic_supported_continue_TRAIN_VALIDATION_only"
        if survives
        else "R5_B1_limited_diagnostic_not_supported_close_B1"
    )
    return {
        "schema_id": "factorlab_r5_b1_limited_diagnostic_receipt@1.0",
        "research_identity": "R5_multiscale_serial_dependence_state_v1_B1_limited_diagnostic",
        "historical_frozen_commit": EXPECTED_FROZEN_COMMIT,
        "historical_runner_git_blob": EXPECTED_RUNNER_BLOB,
        "historical_data_sha256": EXPECTED_OLD_DATA_SHA256,
        "current_data_identity": identity,
        "TRAIN_rows": int(len(train)),
        "VALIDATION_rows": int(len(val)),
        "daily_breadth": breadth,
        "anti_persistence_monotonic_shape": shape,
        "adjudication": adjudication,
        "BLACKBOX_read": False,
        "post_2020_rows_read": False,
        "PnL_read": False,
        "production_authority": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--current-data-root", type=Path, required=True)
    p.add_argument("--frozen-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = run(args.current_data_root, args.frozen_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
