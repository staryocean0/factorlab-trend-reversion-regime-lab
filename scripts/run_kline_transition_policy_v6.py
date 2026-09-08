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
from regime_lab.kline_recognizer_hysteresis_v5 import V4_LINEAR_CONFIG, linear_probabilities
from regime_lab.kline_recognizer_optimization_v4 import fit_model, serialize_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_transition_policy_v6 import (
    aggregate_fold_metrics,
    diagnostic_success,
    frozen_transition_policy_menu,
    frozen_v5_baseline,
    score_policy_period_from_probabilities,
    select_transition_policy,
)
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_TRANSITION_POLICY_V6_PROTOCOL.md"
V5_SUMMARY_PATH = ROOT / "experiments/kline_recognizer_hysteresis_v5/summary.json"
V5_RESULT_COMMIT = "e4ddffd3c190ba18739587aabf73844b3daa2230"


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


def _candidate_row(policy, fold_results, aggregate):
    row: dict[str, object] = {
        "candidate_id": policy.candidate_id,
        "universal_baseline": policy.universal_baseline,
        **aggregate,
    }
    for kind in ("trend_to_range", "range_to_trend", "enter_shock", "exit_shock"):
        rule = getattr(policy, kind)
        row[f"{kind}_margin"] = rule.margin
        row[f"{kind}_min_probability"] = rule.min_probability
        row[f"{kind}_confirmation_bars"] = rule.confirmation_bars
    for fold_name, assets in fold_results.items():
        for symbol, metrics in assets.items():
            prefix = f"{fold_name}_{symbol.replace('.', '_')}"
            for metric in (
                "balanced_accuracy_4state",
                "macro_f1_4state",
                "transition_precision",
                "transition_recall",
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
        for role, source in (("v6_selected", selected), ("v5_universal", baseline)):
            row = {"symbol": symbol, "role": role}
            row.update(source[symbol])
            rows.append(row)
    return pd.DataFrame(rows)


def _result_card(policy, aggregate, selected_2025, baseline_2025, success, typed_available):
    lines = [
        "# K-line recognizer transition policy v6 — result card",
        "",
        "V6 modifies only recognizer A's state-switch policy. Classifier, features and frozen benchmark are unchanged.",
        "",
        "## Selected transition policy",
        "",
        f"- candidate: `{policy.candidate_id}`",
        f"- typed candidate available under point floors: `{typed_available}`",
        "",
    ]
    for label, attr in (
        ("Trend -> Range", "trend_to_range"),
        ("Range -> Trend", "range_to_trend"),
        ("Enter Shock", "enter_shock"),
        ("Exit Shock", "exit_shock"),
    ):
        rule = getattr(policy, attr)
        lines.append(
            f"- {label}: margin `{rule.margin:.2f}`, min probability `{rule.min_probability:.2f}`, confirmation `{rule.confirmation_bars}` bars"
        )
    lines.extend(
        [
            "",
            "Selection used only rolling pre-2025 folds (2022, 2023, 2024).",
            "",
            "## Cross-validation worst-cell summary",
            "",
            f"- minimum balanced accuracy: `{float(aggregate['min_balanced_accuracy']):.3f}`",
            f"- minimum macro F1: `{float(aggregate['min_macro_f1']):.3f}`",
            f"- minimum transition F1: `{float(aggregate['min_transition_f1']):.3f}`",
            f"- maximum false transitions/day: `{float(aggregate['max_false_transitions_per_day']):.3f}`",
            "",
            "## 2025 consumed-data diagnostic",
            "",
            "| Asset | Policy | Balanced accuracy | Macro F1 | Transition precision | Transition recall | Transition F1 | False transitions/day |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for symbol in ("000852.SH", "000688.SH"):
        for label, source in (("v6 selected", selected_2025), ("v5 universal", baseline_2025)):
            m = source[symbol]
            lines.append(
                f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_precision']):.3f} | "
                f"{float(m['transition_recall']):.3f} | {float(m['transition_f1']):.3f} | "
                f"{float(m['false_transitions_per_day']):.3f} |"
            )
    lines.extend(["", "## Adjudication", "", f"Outcome: **{success['status']}**", ""])
    if success["failures"]:
        lines.append("Useful-improvement gates failed:")
        lines.extend(f"- {item}" for item in success["failures"])
        lines.append("")
    if success["strong_target_passed"]:
        lines.append("The stronger target (transition F1 >= 0.30 and false transitions/day <= 0.80 on both assets) also passed.")
    else:
        lines.append("Stronger target not yet passed:")
        lines.extend(f"- {item}" for item in success["strong_target_failures"])
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "2025 was already consumed by earlier development and is diagnostic only. This result is about chart-state recognition, not trading profitability or fresh OOS performance.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen v6 type-specific transition-policy optimization.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_transition_policy_v6",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    if not V5_SUMMARY_PATH.is_file():
        raise RuntimeError("immutable v5 result bundle is required")

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

    # Fit the unchanged linear C=1 model once per rolling fold and cache probabilities.
    fold_probabilities: dict[str, dict[str, pd.DataFrame]] = {}
    for fold_name, train_end, validation_start, validation_end in FOLDS:
        model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if model is None:
            raise RuntimeError("locked v6 linear model unexpectedly absent")
        fold_probabilities[fold_name] = {
            symbol: linear_probabilities(frame, model) for symbol, frame in frames.items()
        }

    candidate_rows = []
    selection_rows = []
    all_fold_results: dict[str, dict[str, object]] = {}
    for policy in frozen_transition_policy_menu():
        fold_results: dict[str, dict[str, dict[str, object]]] = {}
        for fold_name, _, validation_start, validation_end in FOLDS:
            results, _, _ = score_policy_period_from_probabilities(
                frames,
                fold_probabilities[fold_name],
                judge_events,
                policy,
                start=validation_start,
                end=validation_end,
            )
            fold_results[fold_name] = results
        aggregate = aggregate_fold_metrics(fold_results)
        candidate_rows.append(_candidate_row(policy, fold_results, aggregate))
        selection_rows.append((policy, aggregate))
        all_fold_results[policy.candidate_id] = {"aggregate": aggregate, "folds": fold_results}

    selected_policy, selected_aggregate, typed_available = select_transition_policy(selection_rows)
    selected_folds = all_fold_results[selected_policy.candidate_id]["folds"]

    # Lock policy before referencing the 2025 diagnostic.
    refit_model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
    if refit_model is None:
        raise RuntimeError("v6 refit model unexpectedly absent")
    refit_probabilities = {
        symbol: linear_probabilities(frame, refit_model) for symbol, frame in frames.items()
    }
    selected_2025, per_state_selected, transitions_selected = score_policy_period_from_probabilities(
        frames,
        refit_probabilities,
        judge_events,
        selected_policy,
        start=DIAGNOSTIC_START,
        end=DIAGNOSTIC_END,
    )
    baseline_policy = frozen_v5_baseline()
    baseline_2025, _, _ = score_policy_period_from_probabilities(
        frames,
        refit_probabilities,
        judge_events,
        baseline_policy,
        start=DIAGNOSTIC_START,
        end=DIAGNOSTIC_END,
    )
    success = diagnostic_success(selected_2025, baseline_2025)

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
        "status": "complete_type_specific_transition_policy_tuning",
        "adjudication": success,
        "selected_policy": selected_policy.to_dict(),
        "selected_policy_id": selected_policy.candidate_id,
        "typed_candidate_available_under_point_floors": bool(typed_available),
        "cross_validation_aggregate": selected_aggregate,
        "cross_validation_folds": selected_folds,
        "diagnostic_2025_selected": selected_2025,
        "diagnostic_2025_v5_universal": baseline_2025,
        "candidate_count": len(candidate_rows),
        "2025_used_for_selection": False,
        "2025_is_fresh_oos": False,
    }
    selected_recognizer = {
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
        "v5_result_commit": V5_RESULT_COMMIT,
        "v5_summary_sha256": _sha256(V5_SUMMARY_PATH),
        "market_ranges": market_ranges,
        "folds": FOLDS,
        "diagnostic_2025": [DIAGNOSTIC_START, DIAGNOSTIC_END],
        "2026_excluded": True,
    }

    candidate_table.to_csv(output_dir / "candidate_cv.csv", index=False)
    diagnostic_table.to_csv(output_dir / "diagnostic_2025.csv", index=False)
    per_state.to_csv(output_dir / "per_state_2025.csv", index=False)
    transitions.to_csv(output_dir / "transition_events_2025.csv", index=False)
    _write_json(output_dir / "selected_recognizer.json", selected_recognizer)
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "input_identity.json", input_identity)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(
            selected_policy,
            selected_aggregate,
            selected_2025,
            baseline_2025,
            success,
            typed_available,
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
        "schema": "kline_recognizer_transition_policy_v6_execution_receipt@1.0",
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
