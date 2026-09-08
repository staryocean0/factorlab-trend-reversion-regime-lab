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

from regime_lab.kline_independent_judge_v3 import (
    INDEPENDENT_JUDGE_RADIUS,
    INDEPENDENT_JUDGE_WINDOW,
    INDEPENDENT_REFERENCE_HISTORY,
    independent_agreement_grade,
    score_independent_judge,
)
from regime_lab.kline_state_recognition import ALL_STATES, CONCRETE_STATES, RecognitionConfig, build_state_timeseries
from regime_lab.market_data import ROOT, load_market_data

SYMBOL_RANGES = {
    "000852.SH": ("2015-01-05", "2025-12-31"),
    "000688.SH": ("2020-07-23", "2025-12-31"),
}
PROTOCOL_PATH = ROOT / "docs/research/KLINE_INDEPENDENT_JUDGE_V3_PROTOCOL.md"
V2_SUMMARY_PATH = ROOT / "experiments/kline_transition_recognition_v2/summary.json"
V2_RESULT_COMMIT = "f5531a47a7de1cb89f0a1190694f56e1c5136a87"


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _git_head(root: Path, override: str | None) -> str:
    if override:
        return override
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True)
    return result.stdout.strip()


def _packages() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = "not-installed"
    return out


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
    path.write_text(json.dumps(_clean(payload), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _confusion_long(symbol: str, confusion: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for truth in CONCRETE_STATES:
        for prediction in ALL_STATES:
            rows.append(
                {
                    "symbol": symbol,
                    "independent_judge_state": truth,
                    "predicted_state": prediction,
                    "count": int(confusion.at[truth, prediction]) if not confusion.empty else 0,
                }
            )
    return pd.DataFrame(rows)


def _year_stability(yearly: pd.DataFrame) -> dict[str, object]:
    if yearly.empty:
        return {"eligible_year_count": 0, "yearly_balanced_accuracy_median": math.nan, "yearly_balanced_accuracy_min": math.nan}
    eligible = yearly.loc[(yearly["n_scored"] >= 500) & (yearly["min_state_support"] >= 20) & yearly["balanced_accuracy_4state"].notna()]
    return {
        "eligible_year_count": int(len(eligible)),
        "yearly_balanced_accuracy_median": float(eligible["balanced_accuracy_4state"].median()) if not eligible.empty else math.nan,
        "yearly_balanced_accuracy_min": float(eligible["balanced_accuracy_4state"].min()) if not eligible.empty else math.nan,
    }


def _result_card(grade: dict[str, object], assets: dict[str, dict[str, object]], v2_assets: dict[str, dict[str, object]]) -> str:
    lines = [
        "# K-line independent judge v3 — result card",
        "",
        f"Independent algorithmic agreement: **{grade.get('grade', 'inconclusive')}**",
        "",
        "This v3 judge is structurally different from the recognizer: it uses an 80-minute centered OHLC geometry view based on line fit, channel displacement/location, turning points and high-low range expansion. It does not use BDCI, DII, signed efficiency or realized volatility.",
        "",
        "## Independent-judge score",
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
    lines.extend(["", "## Same-family v2 internal score (context only)", "", "| Asset | V2 balanced accuracy | V2 transition F1 |", "|---|---:|---:|"])
    for symbol in ("000852.SH", "000688.SH"):
        row = v2_assets[symbol]
        lines.append("| {s} | {b:.3f} | {t:.3f} |".format(s=symbol, b=float(row.get("balanced_accuracy_4state", math.nan)), t=float(row.get("transition_f1", math.nan))))
    lines.extend(["", "## Adjudication", "", f"Reason: {grade.get('reason', '')}", ""])
    failures = grade.get("failures", [])
    if isinstance(failures, list) and failures:
        lines.append("Failed gates:")
        lines.extend(f"- {item}" for item in failures)
        lines.append("")
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This is an independent **algorithmic** judge, not independent human annotation. A positive result supports robustness to a different chart description, but still does not establish human-equivalent recognition, fresh OOS validity, trading profitability, production routing, or Level 5.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen independent K-line judge v3.")
    parser.add_argument("--code-commit")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "experiments/kline_independent_judge_v3")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(ROOT, args.code_commit)
    config = RecognitionConfig()

    if not V2_SUMMARY_PATH.is_file():
        raise RuntimeError("v2 result bundle is required as immutable comparison evidence")
    v2_summary = json.loads(V2_SUMMARY_PATH.read_text())
    v2_assets = v2_summary["assets"]

    state_parts: list[pd.DataFrame] = []
    confusion_parts: list[pd.DataFrame] = []
    per_state_parts: list[pd.DataFrame] = []
    yearly_parts: list[pd.DataFrame] = []
    transition_parts: list[pd.DataFrame] = []
    asset_results: dict[str, dict[str, object]] = {}
    audits: dict[str, object] = {}
    market_ranges: dict[str, object] = {}

    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        if market.empty:
            raise RuntimeError(f"verified 5m market data empty for {symbol}")
        state_timeseries = build_state_timeseries(market, config=config)
        summary, confusion, per_state, yearly, transitions, audit, judged_frame = score_independent_judge(state_timeseries, config=config)
        asset_results[symbol] = {
            **summary,
            "min_state_support": int(per_state["support"].min()) if not per_state.empty else 0,
            **_year_stability(yearly),
        }
        audits[symbol] = audit
        market_ranges[symbol] = {"frequency": "5m", "start": start, "end": end, "market_rows": int(len(market)), "state_rows": int(len(state_timeseries))}

        export_cols = [
            "symbol", "trading_day", "market_time_shanghai", "recognition_eligible",
            "online_state", "online_decoded_state_v3",
            "independent_judge_center_eligible", "independent_judge_center_state",
            "independent_v3_score_eligible", "independent_judge_available_state",
            "independent_linear_r", "independent_channel_displacement",
            "independent_terminal_channel_location", "independent_turning_point_density",
            "independent_centered_median_log_range", "independent_centered_max_log_range",
            "independent_median_range_rank_prior480", "independent_max_range_rank_prior480",
        ]
        state_parts.append(judged_frame[export_cols].copy())
        confusion_parts.append(_confusion_long(symbol, confusion))
        per_state_parts.append(per_state.assign(symbol=symbol))
        yearly_parts.append(yearly.assign(symbol=symbol))
        transition_parts.append(transitions.assign(symbol=symbol))

    grade = independent_agreement_grade(asset_results)
    judge_timeseries = pd.concat(state_parts, ignore_index=True)
    confusion_matrix = pd.concat(confusion_parts, ignore_index=True)
    per_state_metrics = pd.concat(per_state_parts, ignore_index=True)
    yearly_metrics = pd.concat(yearly_parts, ignore_index=True)
    transition_events = pd.concat(transition_parts, ignore_index=True, sort=False)

    manifest = ROOT / "data/manifest.json"
    protocol_sha = _sha256(PROTOCOL_PATH)
    input_identity = {
        "code_commit": code_commit,
        "protocol_sha256": protocol_sha,
        "market_manifest_sha256": _sha256(manifest),
        "market_ranges": market_ranges,
        "v2_result_commit": V2_RESULT_COMMIT,
        "v2_summary_sha256": _sha256(V2_SUMMARY_PATH),
        "data_role": "consumed_development_material",
        "2026_excluded": True,
    }
    judge_contract = {
        "schema": "kline_independent_judge_v3_contract@1.0",
        "clock": "5m",
        "centered_window_bars": INDEPENDENT_JUDGE_WINDOW,
        "radius_bars": INDEPENDENT_JUDGE_RADIUS,
        "reference_history": INDEPENDENT_REFERENCE_HISTORY,
        "features": [
            "linear_r", "channel_displacement", "terminal_channel_location",
            "turning_point_density", "centered_median_log_range",
            "centered_max_log_range", "strict_prior_range_ranks",
        ],
        "forbidden": [
            "BDCI", "DII", "signed_efficiency", "realized_volatility",
            "online_state_as_judge_input", "v1_or_v2_oracle", "forward_return", "PnL", "2026", "UK_alert",
        ],
        "thresholds": {
            "shock_median_range_rank": 0.95,
            "shock_max_range_rank": 0.995,
            "trend_abs_linear_r": 0.70,
            "trend_abs_channel_displacement": 0.40,
            "trend_terminal_location_up": 0.70,
            "trend_terminal_location_down": 0.30,
            "trend_max_turning_density": 0.45,
            "range_max_abs_linear_r": 0.40,
            "range_max_abs_channel_displacement": 0.30,
            "range_min_turning_density": 0.35,
        },
    }
    summary_payload = {
        "status": "complete_independent_algorithmic_judge_score",
        "grade": grade,
        "assets": asset_results,
        "v2_same_family_internal_assets": v2_assets,
        "level_5_available": False,
        "human_annotation_used": False,
    }

    judge_timeseries.to_csv(output_dir / "judge_timeseries.csv", index=False)
    confusion_matrix.to_csv(output_dir / "confusion_matrix.csv", index=False)
    per_state_metrics.to_csv(output_dir / "per_state_metrics.csv", index=False)
    yearly_metrics.to_csv(output_dir / "yearly_metrics.csv", index=False)
    transition_events.to_csv(output_dir / "transition_events.csv", index=False)
    _write_json(output_dir / "summary.json", summary_payload)
    _write_json(output_dir / "input_identity.json", input_identity)
    _write_json(output_dir / "judge_contract.json", judge_contract)
    _write_json(output_dir / "availability_audit.json", audits)
    (output_dir / "RESULT_CARD.md").write_text(_result_card(grade, asset_results, v2_assets), encoding="utf-8")

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md", "summary.json", "input_identity.json", "judge_contract.json",
        "judge_timeseries.csv", "confusion_matrix.csv", "per_state_metrics.csv",
        "yearly_metrics.csv", "transition_events.csv", "availability_audit.json",
    ]
    receipt = {
        "schema": "kline_independent_judge_v3_execution_receipt@1.0",
        "code_commit": code_commit,
        "protocol_sha256": protocol_sha,
        "command": " ".join(sys.argv),
        "cwd": os.getcwd(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "packages": _packages(),
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