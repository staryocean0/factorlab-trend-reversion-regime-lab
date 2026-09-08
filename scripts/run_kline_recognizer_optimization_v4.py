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

from regime_lab.kline_independent_judge_v3 import build_independent_judge_frame
from regime_lab.kline_recognizer_optimization_v4 import (
    CandidateConfig,
    fit_model,
    frozen_candidate_menu,
    holdout_success,
    score_config_period,
    select_candidate,
    serialize_model,
)
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.market_data import ROOT, load_market_data

SYMBOL_RANGES = {
    "000852.SH": ("2015-01-05", "2025-12-31"),
    "000688.SH": ("2020-07-23", "2025-12-31"),
}
TRAIN_END = "2022-12-31"
VALIDATION_START = "2023-01-01"
VALIDATION_END = "2024-12-31"
REFIT_END = "2024-12-31"
HOLDOUT_START = "2025-01-01"
HOLDOUT_END = "2025-12-31"
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_OPTIMIZATION_V4_PROTOCOL.md"
V3_SUMMARY_PATH = ROOT / "experiments/kline_independent_judge_v3/summary.json"
V3_RESULT_COMMIT = "c6487eab13fca2cd79a0c1c30fbc41c4943eede5"


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
    versions: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


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


def _candidate_id(config: CandidateConfig) -> str:
    if config.family == "linear":
        return f"linear_C{config.C:g}_confirm{config.confirmation_bars}"
    return f"{config.family}_confirm{config.confirmation_bars}"


def _validation_row(config: CandidateConfig, results: dict[str, dict[str, object]]) -> dict[str, object]:
    row: dict[str, object] = {
        "candidate": _candidate_id(config),
        "family": config.family,
        "C": config.C,
        "confirmation_bars": config.confirmation_bars,
    }
    for symbol in ("000852.SH", "000688.SH"):
        prefix = symbol.replace(".", "_")
        metrics = results[symbol]
        for metric in (
            "balanced_accuracy_4state",
            "macro_f1_4state",
            "exact_accuracy_including_abstention",
            "online_concrete_coverage",
            "transition_precision",
            "transition_recall",
            "transition_f1",
            "false_transitions_per_day",
        ):
            row[f"{prefix}_{metric}"] = metrics.get(metric)
    row["min_balanced_accuracy"] = min(
        float(results[s]["balanced_accuracy_4state"]) for s in ("000852.SH", "000688.SH")
    )
    row["min_macro_f1"] = min(float(results[s]["macro_f1_4state"]) for s in ("000852.SH", "000688.SH"))
    row["min_transition_f1"] = min(float(results[s]["transition_f1"]) for s in ("000852.SH", "000688.SH"))
    row["mean_false_transitions_per_day"] = sum(
        float(results[s]["false_transitions_per_day"]) for s in ("000852.SH", "000688.SH")
    ) / 2.0
    return row


def _flatten_holdout(
    optimized: dict[str, dict[str, object]], baseline: dict[str, dict[str, object]]
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for symbol in ("000852.SH", "000688.SH"):
        for role, source in (("optimized", optimized), ("v3_baseline", baseline)):
            row = {"symbol": symbol, "role": role}
            row.update(source[symbol])
            rows.append(row)
    return pd.DataFrame(rows)


def _result_card(
    selected: CandidateConfig,
    validation: dict[str, dict[str, object]],
    optimized: dict[str, dict[str, object]],
    baseline: dict[str, dict[str, object]],
    success: dict[str, object],
) -> str:
    lines = [
        "# K-line recognizer optimization v4 — result card",
        "",
        f"Outcome: **{success['status']}**",
        "",
        "V4 directly optimizes one recognizer. The v3 independent judge is frozen as the target/benchmark; no new evaluator layer is introduced.",
        "",
        "## Selected recognizer",
        "",
        f"- family: `{selected.family}`",
        f"- confirmation bars: `{selected.confirmation_bars}`",
        f"- C: `{selected.C}`" if selected.C is not None else "- C: n/a",
        "",
        "Selected only on 2023-2024 validation. The configuration was then locked, refit through 2024 when applicable, and evaluated once on 2025.",
        "",
        "## Validation score used for selection",
        "",
        "| Asset | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |",
        "|---|---:|---:|---:|---:|",
    ]
    for symbol in ("000852.SH", "000688.SH"):
        row = validation[symbol]
        lines.append(
            f"| {symbol} | {float(row['balanced_accuracy_4state']):.3f} | {float(row['macro_f1_4state']):.3f} | {float(row['transition_f1']):.3f} | {float(row['false_transitions_per_day']):.3f} |"
        )
    lines.extend(
        [
            "",
            "## 2025 temporal holdout",
            "",
            "| Asset | Model | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day | Exact accuracy |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for symbol in ("000852.SH", "000688.SH"):
        for label, source in (("optimized", optimized), ("v3 baseline", baseline)):
            row = source[symbol]
            lines.append(
                f"| {symbol} | {label} | {float(row['balanced_accuracy_4state']):.3f} | {float(row['macro_f1_4state']):.3f} | {float(row['transition_f1']):.3f} | {float(row['false_transitions_per_day']):.3f} | {float(row['exact_accuracy_including_abstention']):.3f} |"
            )
    failures = success.get("failures", [])
    lines.extend(["", "## Adjudication", ""])
    if failures:
        lines.append("Frozen improvement gates not all passed:")
        lines.extend(f"- {item}" for item in failures)
    else:
        lines.append("All frozen v4 improvement gates passed on both assets in the 2025 holdout.")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "2025 is a temporal holdout inside already-consumed historical material, not fresh future OOS. This is chart-state recognition optimization, not a profitability or live-trading claim.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Directly optimize and holdout-test the K-line recognizer v4.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_optimization_v4",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(ROOT, args.code_commit)

    frames: dict[str, pd.DataFrame] = {}
    judge_events: dict[str, pd.DataFrame] = {}
    market_ranges: dict[str, object] = {}
    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        state_timeseries = build_state_timeseries(market, config=RecognitionConfig())
        judge_frame, _, center_events = build_independent_judge_frame(
            state_timeseries, config=RecognitionConfig()
        )
        frames[symbol] = judge_frame
        judge_events[symbol] = center_events
        market_ranges[symbol] = {
            "frequency": "5m",
            "start": start,
            "end": end,
            "market_rows": int(len(market)),
            "judge_frame_rows": int(len(judge_frame)),
        }

    # Hard separation: selection receives only rows through 2024.
    selection_frames = {
        symbol: frame.loc[pd.to_datetime(frame["trading_day"]) <= pd.Timestamp(VALIDATION_END)].copy()
        for symbol, frame in frames.items()
    }
    selection_judge_events = {
        symbol: events.loc[pd.to_datetime(events["trading_day"]) <= pd.Timestamp(VALIDATION_END)].copy()
        if not events.empty
        else events.copy()
        for symbol, events in judge_events.items()
    }

    model_cache: dict[tuple[str, float | None], dict[str, object] | None] = {}
    validation_rows: list[dict[str, object]] = []
    selection_rows: list[tuple[CandidateConfig, dict[str, dict[str, object]]]] = []
    validation_detail: dict[str, dict[str, dict[str, object]]] = {}

    for candidate in frozen_candidate_menu():
        cache_key = (candidate.family, candidate.C)
        if cache_key not in model_cache:
            model_cache[cache_key] = fit_model(
                selection_frames,
                candidate,
                start=None,
                end=TRAIN_END,
            )
        model = model_cache[cache_key]
        results, _, _ = score_config_period(
            selection_frames,
            selection_judge_events,
            candidate,
            model,
            start=VALIDATION_START,
            end=VALIDATION_END,
        )
        selection_rows.append((candidate, results))
        validation_rows.append(_validation_row(candidate, results))
        validation_detail[_candidate_id(candidate)] = results

    selected, selected_validation = select_candidate(selection_rows)
    selected_id = _candidate_id(selected)

    # Selection is now locked. Only after this line may the 2025 holdout be referenced.
    refit_model = fit_model(
        selection_frames,
        selected,
        start=None,
        end=REFIT_END,
    )
    optimized_holdout, optimized_per_state, optimized_transitions = score_config_period(
        frames,
        judge_events,
        selected,
        refit_model,
        start=HOLDOUT_START,
        end=HOLDOUT_END,
    )

    baseline_config = CandidateConfig("rule", 2)
    baseline_holdout, _, _ = score_config_period(
        frames,
        judge_events,
        baseline_config,
        None,
        start=HOLDOUT_START,
        end=HOLDOUT_END,
    )
    success = holdout_success(optimized_holdout, baseline_holdout)

    validation_table = pd.DataFrame(validation_rows)
    holdout_table = _flatten_holdout(optimized_holdout, baseline_holdout)
    per_state = pd.concat(
        [table.assign(symbol=symbol) for symbol, table in optimized_per_state.items()],
        ignore_index=True,
    )
    transition_events = pd.concat(
        [table.assign(symbol=symbol) for symbol, table in optimized_transitions.items()],
        ignore_index=True,
        sort=False,
    )

    selected_model_payload = {
        "candidate_id": selected_id,
        "config": selected.to_dict(),
        "model": serialize_model(refit_model),
        "selection_period": [VALIDATION_START, VALIDATION_END],
        "refit_data_end": REFIT_END,
        "holdout_period": [HOLDOUT_START, HOLDOUT_END],
        "selection_rule": "lexicographic worst-asset balanced_accuracy, macro_f1, transition_f1, then false transitions/day",
    }
    summary = {
        "status": success["status"],
        "adjudication": success,
        "selected_candidate": selected.to_dict(),
        "selected_candidate_id": selected_id,
        "validation_assets": selected_validation,
        "holdout_assets": optimized_holdout,
        "holdout_v3_baseline_assets": baseline_holdout,
        "candidate_count": len(validation_rows),
        "2025_used_for_selection": False,
        "fresh_oos": False,
    }
    input_identity = {
        "code_commit": code_commit,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "market_manifest_sha256": _sha256(ROOT / "data/manifest.json"),
        "v3_result_commit": V3_RESULT_COMMIT,
        "v3_summary_sha256": _sha256(V3_SUMMARY_PATH),
        "market_ranges": market_ranges,
        "train_end": TRAIN_END,
        "validation": [VALIDATION_START, VALIDATION_END],
        "holdout": [HOLDOUT_START, HOLDOUT_END],
        "2026_excluded": True,
    }

    validation_table.to_csv(output_dir / "candidate_validation.csv", index=False)
    holdout_table.to_csv(output_dir / "holdout_metrics.csv", index=False)
    per_state.to_csv(output_dir / "per_state_metrics.csv", index=False)
    transition_events.to_csv(output_dir / "transition_events.csv", index=False)
    _write_json(output_dir / "selected_model.json", selected_model_payload)
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "input_identity.json", input_identity)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(selected, selected_validation, optimized_holdout, baseline_holdout, success),
        encoding="utf-8",
    )

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "candidate_validation.csv",
        "holdout_metrics.csv",
        "per_state_metrics.csv",
        "transition_events.csv",
        "selected_model.json",
        "summary.json",
        "input_identity.json",
    ]
    receipt = {
        "schema": "kline_recognizer_optimization_v4_execution_receipt@1.0",
        "code_commit": code_commit,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
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
    print(json.dumps(_clean(summary), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
