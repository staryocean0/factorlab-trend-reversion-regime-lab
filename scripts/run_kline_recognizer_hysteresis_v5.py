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
from regime_lab.kline_recognizer_hysteresis_v5 import (
    V4_LINEAR_CONFIG,
    V4_POLICY,
    aggregate_policy_metrics,
    frozen_hysteresis_menu,
    score_policy_period,
    select_hysteresis_policy,
)
from regime_lab.kline_recognizer_optimization_v4 import fit_model, serialize_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.market_data import ROOT, load_market_data

SYMBOL_RANGES = {
    "000852.SH": ("2015-01-05", "2025-12-31"),
    "000688.SH": ("2020-07-23", "2025-12-31"),
}
FOLDS = (
    ("fold_2022", "2021-12-31", "2022-01-01", "2022-12-31"),
    ("fold_2023", "2022-12-31", "2023-01-01", "2023-12-31"),
    ("fold_2024", "2023-12-31", "2024-01-01", "2024-12-31"),
)
REFIT_END = "2024-12-31"
DIAGNOSTIC_START = "2025-01-01"
DIAGNOSTIC_END = "2025-12-31"
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_HYSTERESIS_V5_PROTOCOL.md"
V4_RESULT_PATH = ROOT / "experiments/kline_recognizer_optimization_v4/summary.json"
V4_RESULT_COMMIT = "40e1a35bf134fd7eb9191a4537a9a2eea7f58a9c"


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _git_head(override: str | None) -> str:
    if override:
        return override
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    )
    return result.stdout.strip()


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


def _package_versions() -> dict[str, str]:
    out: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = "not-installed"
    return out


def _policy_id(policy) -> str:
    return (
        f"margin{policy.switch_margin:.2f}_minp{policy.min_new_probability:.2f}_"
        f"confirm{policy.confirmation_bars}"
    )


def _candidate_row(policy, fold_results, aggregate):
    row: dict[str, object] = {"policy": _policy_id(policy), **policy.to_dict(), **aggregate}
    for fold_name, assets in fold_results.items():
        for symbol, metrics in assets.items():
            prefix = f"{fold_name}_{symbol.replace('.', '_')}"
            for metric in (
                "balanced_accuracy_4state",
                "macro_f1_4state",
                "transition_f1",
                "false_transitions_per_day",
                "exact_accuracy_including_abstention",
                "online_concrete_coverage",
            ):
                row[f"{prefix}_{metric}"] = metrics.get(metric)
    return row


def _diagnostic_table(selected, baseline):
    rows = []
    for symbol in ("000852.SH", "000688.SH"):
        for role, source in (("v5_selected", selected), ("v4_policy", baseline)):
            row = {"symbol": symbol, "role": role}
            row.update(source[symbol])
            rows.append(row)
    return pd.DataFrame(rows)


def _result_card(selected_policy, selected_aggregate, selected_folds, selected_2025, baseline_2025, eligible):
    lines = [
        "# K-line recognizer hysteresis v5 — result card",
        "",
        "V5 modifies the same recognizer A. It does not add another evaluator layer.",
        "",
        "## Selected probability-switch policy",
        "",
        f"- switch margin: `{selected_policy.switch_margin:.2f}`",
        f"- minimum new-state probability: `{selected_policy.min_new_probability:.2f}`",
        f"- confirmation bars: `{selected_policy.confirmation_bars}`",
        f"- point-state floor eligibility: `{eligible}`",
        "",
        "Selection used only rolling pre-2025 folds (2022, 2023, 2024).",
        "",
        "## Cross-validation worst-cell summary",
        "",
        f"- minimum balanced accuracy: `{selected_aggregate['min_balanced_accuracy']:.3f}`",
        f"- minimum macro F1: `{selected_aggregate['min_macro_f1']:.3f}`",
        f"- minimum transition F1: `{selected_aggregate['min_transition_f1']:.3f}`",
        f"- maximum false transitions/day: `{selected_aggregate['max_false_transitions_per_day']:.3f}`",
        "",
        "## 2025 consumed-data diagnostic (not a new holdout)",
        "",
        "| Asset | Policy | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day | Exact accuracy |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for symbol in ("000852.SH", "000688.SH"):
        for label, source in (("v5 selected", selected_2025), ("v4 policy", baseline_2025)):
            m = source[symbol]
            lines.append(
                f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_f1']):.3f} | "
                f"{float(m['false_transitions_per_day']):.3f} | "
                f"{float(m['exact_accuracy_including_abstention']):.3f} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation boundary",
            "",
            "The selected hysteresis parameters were not chosen on 2025. However 2025 was already inspected in v4, so the 2025 comparison is development diagnostic evidence only, not fresh OOS validation.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run rolling-CV probability hysteresis optimization for recognizer A.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_hysteresis_v5",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    frames: dict[str, pd.DataFrame] = {}
    judge_events: dict[str, pd.DataFrame] = {}
    market_ranges: dict[str, object] = {}
    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        states = build_state_timeseries(market, config=RecognitionConfig())
        judge_frame, _, center_events = build_independent_judge_frame(states, config=RecognitionConfig())
        frames[symbol] = judge_frame
        judge_events[symbol] = center_events
        market_ranges[symbol] = {
            "frequency": "5m",
            "start": start,
            "end": end,
            "rows": int(len(judge_frame)),
        }

    # Fit the locked linear C=1 classifier once per rolling fold.
    fold_models: dict[str, dict[str, object]] = {}
    for fold_name, train_end, _, _ in FOLDS:
        model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if model is None:
            raise RuntimeError("locked v5 linear model unexpectedly absent")
        fold_models[fold_name] = model

    candidate_rows = []
    selection_rows = []
    all_fold_results: dict[str, dict[str, object]] = {}
    for policy in frozen_hysteresis_menu():
        fold_results: dict[str, dict[str, dict[str, object]]] = {}
        for fold_name, _, validation_start, validation_end in FOLDS:
            results, _, _ = score_policy_period(
                frames,
                judge_events,
                fold_models[fold_name],
                policy,
                start=validation_start,
                end=validation_end,
            )
            fold_results[fold_name] = results
        aggregate = aggregate_policy_metrics(fold_results)
        pid = _policy_id(policy)
        all_fold_results[pid] = {"aggregate": aggregate, "folds": fold_results}
        candidate_rows.append(_candidate_row(policy, fold_results, aggregate))
        selection_rows.append((policy, aggregate))

    selected_policy, selected_aggregate, selected_was_eligible = select_hysteresis_policy(selection_rows)
    selected_id = _policy_id(selected_policy)
    selected_folds = all_fold_results[selected_id]["folds"]

    # Policy is locked before any 2025 diagnostic is referenced.
    refit_model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
    if refit_model is None:
        raise RuntimeError("v5 refit model unexpectedly absent")
    selected_2025, per_state_selected, transitions_selected = score_policy_period(
        frames,
        judge_events,
        refit_model,
        selected_policy,
        start=DIAGNOSTIC_START,
        end=DIAGNOSTIC_END,
    )
    baseline_2025, _, _ = score_policy_period(
        frames,
        judge_events,
        refit_model,
        V4_POLICY,
        start=DIAGNOSTIC_START,
        end=DIAGNOSTIC_END,
    )

    candidate_table = pd.DataFrame(candidate_rows)
    diagnostic_table = _diagnostic_table(selected_2025, baseline_2025)
    per_state = pd.concat(
        [table.assign(symbol=symbol) for symbol, table in per_state_selected.items()],
        ignore_index=True,
    )
    transitions = pd.concat(
        [table.assign(symbol=symbol) for symbol, table in transitions_selected.items()],
        ignore_index=True,
        sort=False,
    )

    summary = {
        "status": "complete_direct_recognizer_hysteresis_tuning",
        "selected_policy": selected_policy.to_dict(),
        "selected_policy_id": selected_id,
        "selected_policy_met_point_floors": bool(selected_was_eligible),
        "cross_validation_aggregate": selected_aggregate,
        "cross_validation_folds": selected_folds,
        "diagnostic_2025_selected": selected_2025,
        "diagnostic_2025_v4_policy": baseline_2025,
        "2025_used_for_selection": False,
        "2025_is_fresh_oos": False,
        "candidate_count": len(candidate_rows),
    }
    selected_model = {
        "classifier": "linear",
        "C": 1.0,
        "policy": selected_policy.to_dict(),
        "refit_data_end": REFIT_END,
        "model": serialize_model(refit_model),
    }
    input_identity = {
        "code_commit": code_commit,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "market_manifest_sha256": _sha256(ROOT / "data/manifest.json"),
        "v4_result_commit": V4_RESULT_COMMIT,
        "v4_result_sha256": _sha256(V4_RESULT_PATH),
        "market_ranges": market_ranges,
        "folds": FOLDS,
        "diagnostic_2025": [DIAGNOSTIC_START, DIAGNOSTIC_END],
        "2026_excluded": True,
    }

    candidate_table.to_csv(output_dir / "candidate_cv.csv", index=False)
    diagnostic_table.to_csv(output_dir / "diagnostic_2025.csv", index=False)
    per_state.to_csv(output_dir / "per_state_2025.csv", index=False)
    transitions.to_csv(output_dir / "transition_events_2025.csv", index=False)
    _write_json(output_dir / "selected_recognizer.json", selected_model)
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "input_identity.json", input_identity)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(
            selected_policy,
            selected_aggregate,
            selected_folds,
            selected_2025,
            baseline_2025,
            selected_was_eligible,
        ),
        encoding="utf-8",
    )

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "candidate_cv.csv",
        "diagnostic_2025.csv",
        "per_state_2025.csv",
        "transition_events_2025.csv",
        "selected_recognizer.json",
        "summary.json",
        "input_identity.json",
    ]
    receipt = {
        "schema": "kline_recognizer_hysteresis_v5_execution_receipt@1.0",
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
