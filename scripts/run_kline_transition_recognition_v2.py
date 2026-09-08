from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from regime_lab.kline_state_recognition import (
    ALL_STATES,
    CONCRETE_STATES,
    RecognitionConfig,
    assess_capability_level,
    build_state_timeseries,
)
from regime_lab.kline_transition_recognition_v2 import v2_score
from regime_lab.market_data import ROOT, load_market_data

SYMBOL_RANGES = {
    "000852.SH": ("2015-01-05", "2025-12-31"),
    "000688.SH": ("2020-07-23", "2025-12-31"),
}
PROTOCOL_PATH = ROOT / "docs/research/KLINE_TRANSITION_RECOGNITION_V2_PROTOCOL.md"
V1_SUMMARY_PATH = ROOT / "experiments/kline_state_recognition_v1/summary.json"
V1_RESULT_COMMIT = "cd9353c87101ae5965b71b4f48685f417b5595e2"


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _git_head(root: Path, override: str | None) -> str:
    if override:
        return override
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


def _package_versions() -> dict[str, str]:
    result: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "not-installed"
    return result


def _clean(value: object) -> object:
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean(v) for v in value]
    if isinstance(value, tuple):
        return [_clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(_clean(payload), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _confusion_long(symbol: str, confusion: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for truth in CONCRETE_STATES:
        for prediction in ALL_STATES:
            rows.append(
                {
                    "symbol": symbol,
                    "oracle_available_state": truth,
                    "predicted_state": prediction,
                    "count": int(confusion.at[truth, prediction]) if not confusion.empty else 0,
                }
            )
    return pd.DataFrame(rows)


def _year_stability(yearly: pd.DataFrame) -> dict[str, object]:
    if yearly.empty:
        return {
            "eligible_year_count": 0,
            "eligible_year_balanced_accuracy_median": math.nan,
            "eligible_year_balanced_accuracy_min": math.nan,
        }
    eligible = yearly.loc[
        (yearly["n_scored"] >= 1000)
        & (yearly["min_state_support"] >= 25)
        & yearly["balanced_accuracy_4state"].notna()
    ]
    return {
        "eligible_year_count": int(len(eligible)),
        "eligible_year_balanced_accuracy_median": float(eligible["balanced_accuracy_4state"].median()) if not eligible.empty else math.nan,
        "eligible_year_balanced_accuracy_min": float(eligible["balanced_accuracy_4state"].min()) if not eligible.empty else math.nan,
    }


def _result_card(
    level: dict[str, object],
    assets: dict[str, dict[str, object]],
    v1_assets: dict[str, dict[str, object]],
) -> str:
    lines = [
        "# K-line transition recognition v2 — result card",
        "",
        f"Primary project capability: **{level.get('level', 'inconclusive')}**",
        "",
        "V2 keeps the v1 raw recognizer thresholds unchanged. The primary score aligns the centered offline judge to the time its six future bars are actually observable and applies the frozen two-bar causal persistence decoder.",
        "",
        "## Primary availability-aligned score",
        "",
        "| Asset | Balanced accuracy | Macro F1 | Concrete coverage | Transition F1 | Exact accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for symbol in ("000852.SH", "000688.SH"):
        row = assets[symbol]
        lines.append(
            "| {s} | {b:.3f} | {m:.3f} | {c:.3f} | {t:.3f} | {e:.3f} |".format(
                s=symbol,
                b=float(row.get("balanced_accuracy_4state", math.nan)),
                m=float(row.get("macro_f1_4state", math.nan)),
                c=float(row.get("online_concrete_coverage", math.nan)),
                t=float(row.get("transition_f1", math.nan)),
                e=float(row.get("exact_accuracy_including_abstention", math.nan)),
            )
        )
    lines.extend(["", "## V1 baseline for comparison", "", "| Asset | V1 balanced accuracy | V1 coverage | V1 transition F1 |", "|---|---:|---:|---:|"])
    for symbol in ("000852.SH", "000688.SH"):
        row = v1_assets[symbol]
        lines.append(
            "| {s} | {b:.3f} | {c:.3f} | {t:.3f} |".format(
                s=symbol,
                b=float(row.get("balanced_accuracy_4state", math.nan)),
                c=float(row.get("online_concrete_coverage", math.nan)),
                t=float(row.get("transition_f1", math.nan)),
            )
        )
    lines.extend(["", "## Adjudication", "", f"Reason: {level.get('reason', '')}", ""])
    failures = level.get("failures", [])
    if isinstance(failures, list) and failures:
        lines.append("Failed higher-level gates:")
        lines.extend(f"- {item}" for item in failures)
        lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            "This is consumed historical development evidence. It measures chart-state recognition at matched information availability; it is not a trading-profit score, future-return predictor, production router, or Level-5 independent validation.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen K-line transition recognition v2.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_transition_recognition_v2",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = RecognitionConfig()
    code_commit = _git_head(ROOT, args.code_commit)

    if not V1_SUMMARY_PATH.is_file():
        raise RuntimeError("v1 result bundle is required as declared development evidence")
    v1_summary = json.loads(V1_SUMMARY_PATH.read_text())
    v1_assets = v1_summary["assets"]

    state_parts: list[pd.DataFrame] = []
    transition_parts: list[pd.DataFrame] = []
    confusion_parts: list[pd.DataFrame] = []
    per_state_parts: list[pd.DataFrame] = []
    yearly_parts: list[pd.DataFrame] = []
    asset_results: dict[str, dict[str, object]] = {}
    secondary_results: dict[str, object] = {}
    alignment_audits: dict[str, object] = {}
    market_ranges: dict[str, object] = {}

    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        if market.empty:
            raise RuntimeError(f"empty verified 5m data for {symbol}")
        raw_states = build_state_timeseries(market, config=config)
        summary, confusion, per_state, yearly, transitions, secondary, alignment_audit = v2_score(
            raw_states, config=config
        )
        min_support = int(per_state["support"].min()) if not per_state.empty else 0
        asset_summary = {**summary, "min_state_support": min_support, **_year_stability(yearly)}
        asset_results[symbol] = asset_summary
        secondary_results[symbol] = secondary
        alignment_audits[symbol] = alignment_audit
        market_ranges[symbol] = {
            "frequency": "5m",
            "start": start,
            "end": end,
            "market_rows": int(len(market)),
            "state_rows": int(len(raw_states)),
        }

        # Rebuild v2 frame once for export; scoring itself remains single frozen design.
        from regime_lab.kline_transition_recognition_v2 import build_v2_state_frame

        v2_frame, _, _ = build_v2_state_frame(raw_states, config=config)
        export = v2_frame[
            [
                "symbol",
                "trading_day",
                "market_time_shanghai",
                "recognition_eligible",
                "v2_score_eligible",
                "eligible_ordinal_day",
                "online_state",
                "online_decoded_state",
                "oracle_state",
                "oracle_confirmed_center_state",
                "oracle_available_state",
            ]
        ].copy()
        state_parts.append(export)
        transition_parts.append(transitions.assign(symbol=symbol))
        confusion_parts.append(_confusion_long(symbol, confusion))
        per_state_parts.append(per_state.assign(symbol=symbol))
        yearly_parts.append(yearly.assign(symbol=symbol))

    level = assess_capability_level(asset_results)
    state_timeseries = pd.concat(state_parts, ignore_index=True)
    transition_events = pd.concat(transition_parts, ignore_index=True, sort=False)
    confusion_matrix = pd.concat(confusion_parts, ignore_index=True)
    per_state_metrics = pd.concat(per_state_parts, ignore_index=True)
    yearly_metrics = pd.concat(yearly_parts, ignore_index=True)

    protocol_sha = _sha256(PROTOCOL_PATH)
    manifest_path = ROOT / "data/manifest.json"
    input_identity = {
        "code_commit": code_commit,
        "protocol_path": str(PROTOCOL_PATH),
        "protocol_sha256": protocol_sha,
        "market_manifest_sha256": _sha256(manifest_path),
        "market_ranges": market_ranges,
        "v1_result_commit": V1_RESULT_COMMIT,
        "v1_summary_sha256": _sha256(V1_SUMMARY_PATH),
        "data_role": "consumed_development_material",
        "2026_excluded": True,
    }
    summary_payload = {
        "status": "complete_historical_availability_aligned_recognition_score",
        "capability": level,
        "assets": asset_results,
        "v1_baseline_assets": v1_assets,
        "level_5_available": False,
    }

    state_timeseries.to_csv(output_dir / "state_timeseries.csv", index=False)
    transition_events.to_csv(output_dir / "transition_events.csv", index=False)
    confusion_matrix.to_csv(output_dir / "confusion_matrix.csv", index=False)
    per_state_metrics.to_csv(output_dir / "per_state_metrics.csv", index=False)
    yearly_metrics.to_csv(output_dir / "yearly_metrics.csv", index=False)
    _write_json(output_dir / "summary.json", summary_payload)
    _write_json(output_dir / "input_identity.json", input_identity)
    _write_json(output_dir / "alignment_audit.json", alignment_audits)
    _write_json(output_dir / "secondary_metrics.json", secondary_results)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(level, asset_results, v1_assets), encoding="utf-8"
    )

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "summary.json",
        "input_identity.json",
        "alignment_audit.json",
        "secondary_metrics.json",
        "state_timeseries.csv",
        "transition_events.csv",
        "confusion_matrix.csv",
        "per_state_metrics.csv",
        "yearly_metrics.csv",
    ]
    receipt = {
        "schema": "kline_transition_recognition_v2_execution_receipt@1.0",
        "code_commit": code_commit,
        "protocol_sha256": protocol_sha,
        "command": " ".join(sys.argv),
        "cwd": os.getcwd(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": _package_versions(),
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "exit_code": 0,
        "output_sha256": {name: _sha256(output_dir / name) for name in output_names},
    }
    _write_json(output_dir / "execution_receipt.json", receipt)
    print(json.dumps(_clean(summary_payload), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
