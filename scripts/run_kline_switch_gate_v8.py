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

import numpy as np
import pandas as pd

from regime_lab.kline_independent_judge_v3 import build_independent_judge_frame
from regime_lab.kline_recognizer_hysteresis_v5 import (
    V4_LINEAR_CONFIG,
    linear_probabilities,
    score_policy_period,
)
from regime_lab.kline_recognizer_optimization_v4 import fit_model, serialize_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_switch_gate_v8 import (
    V5_SELECTED_POLICY,
    aggregate_fold_metrics,
    build_switch_feature_frame,
    build_switch_training_rows,
    diagnostic_success,
    fit_switch_gate,
    frozen_switch_gate_menu,
    score_switch_gate_period,
    select_switch_gate_candidate,
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_SWITCH_GATE_V8_PROTOCOL.md"
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


def _candidate_id(candidate) -> str:
    return f"gate_C{candidate.C_gate:g}_thr{candidate.threshold:.2f}_confirm{candidate.switch_confirm}"


def _candidate_row(candidate, fold_results, aggregate):
    row: dict[str, object] = {
        "candidate_id": _candidate_id(candidate),
        **candidate.to_dict(),
        **aggregate,
    }
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


def _result_card(
    selected,
    selected_aggregate,
    v5_aggregate,
    selected_2025,
    v5_2025,
    diagnostic,
    candidate_best_point,
):
    lines = [
        "# K-line recognizer learned switch gate v8 — result card",
        "",
        "V8 modifies only recognizer A by adding a causal learned switch head. The state classifier, causal K-line feature surface, and frozen benchmark remain unchanged.",
        "",
        "## Pre-2025 promotion decision",
        "",
        f"Switch gate promoted over v5: **{selected is not None}**",
        "",
        "V5 frozen rolling-CV baseline:",
        f"- minimum transition F1: `{float(v5_aggregate['min_transition_f1']):.3f}`",
        f"- maximum false transitions/day: `{float(v5_aggregate['max_false_transitions_per_day']):.3f}`",
        f"- minimum balanced accuracy: `{float(v5_aggregate['min_balanced_accuracy']):.3f}`",
        f"- minimum macro F1: `{float(v5_aggregate['min_macro_f1']):.3f}`",
        "",
    ]
    if candidate_best_point is not None:
        c, a = candidate_best_point
        lines.extend(
            [
                "Best point-eligible v8 candidate before promotion gate:",
                f"- candidate: `{_candidate_id(c)}`",
                f"- minimum transition F1: `{float(a['min_transition_f1']):.3f}`",
                f"- maximum false transitions/day: `{float(a['max_false_transitions_per_day']):.3f}`",
                f"- minimum balanced accuracy: `{float(a['min_balanced_accuracy']):.3f}`",
                f"- minimum macro F1: `{float(a['min_macro_f1']):.3f}`",
                "",
            ]
        )
    if selected is None:
        lines.extend(
            [
                "No switch-gate candidate satisfied the preregistered pre-2025 promotion gate. V5 remains the active recognizer; 2025 was not used to rescue v8.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "Selected switch gate:",
                f"- candidate: `{_candidate_id(selected)}`",
                f"- C_gate: `{selected.C_gate}`",
                f"- threshold: `{selected.threshold}`",
                f"- switch confirmation: `{selected.switch_confirm}`",
                f"- init confirmation: `{selected.init_confirm}`",
                f"- pre-2025 minimum transition F1: `{float(selected_aggregate['min_transition_f1']):.3f}`",
                f"- pre-2025 maximum false transitions/day: `{float(selected_aggregate['max_false_transitions_per_day']):.3f}`",
                "",
                "## 2025 consumed-data diagnostic",
                "",
                "| Asset | Policy | Balanced accuracy | Macro F1 | Transition precision | Transition recall | Transition F1 | False transitions/day |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v8 selected", selected_2025), ("v5 universal", v5_2025)):
                m = source[symbol]
                lines.append(
                    f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                    f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_precision']):.3f} | "
                    f"{float(m['transition_recall']):.3f} | {float(m['transition_f1']):.3f} | "
                    f"{float(m['false_transitions_per_day']):.3f} |"
                )
        lines.extend(["", "2025 useful diagnostic passed: **{}**".format(bool(diagnostic["useful_improvement"])), ""])
        if diagnostic["useful_failures"]:
            lines.append("Useful diagnostic failures:")
            lines.extend(f"- {x}" for x in diagnostic["useful_failures"])
            lines.append("")
        if diagnostic["strong_failures"]:
            lines.append("Strong target not yet passed:")
            lines.extend(f"- {x}" for x in diagnostic["strong_failures"])
            lines.append("")
    lines.extend(
        [
            "## Boundary",
            "",
            "2025 was already consumed by earlier development and is diagnostic only. This is chart-state recognition research, not a trading-profitability or fresh-OOS claim.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen learned switch-gate v8 optimization.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_switch_gate_v8",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    if not V5_SUMMARY_PATH.exists():
        raise RuntimeError("immutable v5 result bundle is required")
    v5_summary = json.loads(V5_SUMMARY_PATH.read_text(encoding="utf-8"))
    v5_aggregate = v5_summary["cross_validation_aggregate"]

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

    menu = frozen_switch_gate_menu()
    fold_results_by_candidate: dict[str, dict[str, dict[str, dict[str, object]]]] = {
        _candidate_id(c): {} for c in menu
    }
    candidate_models_meta: dict[str, dict[str, object]] = {}

    for fold_name, train_end, validation_start, validation_end in FOLDS:
        state_model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if state_model is None:
            raise RuntimeError("v8 locked linear state model unexpectedly absent")

        pooled_x: list[np.ndarray] = []
        pooled_y: list[np.ndarray] = []
        for symbol in sorted(frames):
            frame = frames[symbol]
            probs = linear_probabilities(frame, state_model)
            features = build_switch_feature_frame(frame, probs)
            X, y = build_switch_training_rows(frame, features, start=None, end=train_end)
            pooled_x.append(X)
            pooled_y.append(y)
        X_train = np.vstack(pooled_x)
        y_train = np.concatenate(pooled_y)

        gate_models = {
            C: fit_switch_gate(X_train, y_train, C_gate=C)
            for C in (0.1, 1.0, 10.0)
        }
        state_model_map = {symbol: state_model for symbol in frames}
        for candidate in menu:
            cid = _candidate_id(candidate)
            results, _, _ = score_switch_gate_period(
                frames,
                judge_events,
                state_model_map,
                gate_models[candidate.C_gate],
                candidate,
                start=validation_start,
                end=validation_end,
            )
            fold_results_by_candidate[cid][fold_name] = results
        candidate_models_meta[fold_name] = {
            "train_end": train_end,
            "switch_training_rows": int(len(y_train)),
            "switch_positive_rows": int(y_train.sum()),
            "switch_positive_rate": float(np.mean(y_train)),
            "gate_models": {
                str(C): {
                    "optimizer_iterations": int(model["optimizer_iterations"]),
                    "optimizer_loss": float(model["optimizer_loss"]),
                    "positive_rate": float(model["positive_rate"]),
                }
                for C, model in gate_models.items()
            },
        }

    candidate_rows = []
    selection_rows = []
    aggregate_by_candidate: dict[str, dict[str, float]] = {}
    for candidate in menu:
        cid = _candidate_id(candidate)
        folds = fold_results_by_candidate[cid]
        aggregate = aggregate_fold_metrics(folds)
        aggregate_by_candidate[cid] = aggregate
        candidate_rows.append(_candidate_row(candidate, folds, aggregate))
        selection_rows.append((candidate, aggregate))

    selected, selected_aggregate = select_switch_gate_candidate(selection_rows, v5_aggregate)
    point_eligible_rows = [
        (c, a)
        for c, a in selection_rows
        if float(a["min_balanced_accuracy"]) >= 0.75 and float(a["min_macro_f1"]) >= 0.72
    ]
    best_point = None
    if point_eligible_rows:
        best_point = max(
            point_eligible_rows,
            key=lambda item: (
                float(item[1]["min_transition_f1"]),
                -float(item[1]["max_false_transitions_per_day"]),
                float(item[1]["min_balanced_accuracy"]),
                float(item[1]["min_macro_f1"]),
            ),
        )

    selected_2025 = None
    v5_2025 = None
    diagnostic = None
    selected_gate_model = None
    refit_state_model = None
    per_state = pd.DataFrame()
    transitions = pd.DataFrame()

    # Selection is locked before any 2025 diagnostic is referenced.
    if selected is not None:
        refit_state_model = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        if refit_state_model is None:
            raise RuntimeError("v8 refit linear state model unexpectedly absent")
        pooled_x: list[np.ndarray] = []
        pooled_y: list[np.ndarray] = []
        for symbol in sorted(frames):
            frame = frames[symbol]
            probs = linear_probabilities(frame, refit_state_model)
            features = build_switch_feature_frame(frame, probs)
            X, y = build_switch_training_rows(frame, features, start=None, end=REFIT_END)
            pooled_x.append(X)
            pooled_y.append(y)
        X_refit = np.vstack(pooled_x)
        y_refit = np.concatenate(pooled_y)
        selected_gate_model = fit_switch_gate(X_refit, y_refit, C_gate=selected.C_gate)
        state_model_map = {symbol: refit_state_model for symbol in frames}
        selected_2025, per_state_selected, transitions_selected = score_switch_gate_period(
            frames,
            judge_events,
            state_model_map,
            selected_gate_model,
            selected,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        v5_2025, _, _ = score_policy_period(
            frames,
            judge_events,
            refit_state_model,
            V5_SELECTED_POLICY,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        diagnostic = diagnostic_success(selected_2025, v5_2025)
        per_state = pd.concat(
            [table.assign(symbol=symbol) for symbol, table in per_state_selected.items()],
            ignore_index=True,
        )
        transitions = pd.concat(
            [table.assign(symbol=symbol) for symbol, table in transitions_selected.items()],
            ignore_index=True,
            sort=False,
        )

    candidate_table = pd.DataFrame(candidate_rows)
    candidate_table.to_csv(output_dir / "candidate_cv.csv", index=False)
    if not per_state.empty:
        per_state.to_csv(output_dir / "per_state_2025.csv", index=False)
    if not transitions.empty:
        transitions.to_csv(output_dir / "transition_events_2025.csv", index=False)

    summary = {
        "status": "complete_switch_gate_v8",
        "promoted_over_v5_pre2025": selected is not None,
        "selected_candidate": selected.to_dict() if selected is not None else None,
        "selected_candidate_id": _candidate_id(selected) if selected is not None else None,
        "selected_aggregate": selected_aggregate,
        "v5_cross_validation_aggregate": v5_aggregate,
        "best_point_eligible_candidate": (
            {"candidate": best_point[0].to_dict(), "aggregate": best_point[1]}
            if best_point is not None
            else None
        ),
        "diagnostic_2025_selected": selected_2025,
        "diagnostic_2025_v5": v5_2025,
        "diagnostic_adjudication": diagnostic,
        "candidate_count": len(menu),
        "fold_model_audit": candidate_models_meta,
        "2025_used_for_selection": False,
        "2025_is_fresh_oos": False,
    }
    _write_json(output_dir / "summary.json", summary)

    selected_payload = {
        "active_recognizer": "v8_switch_gate" if selected is not None else "v5_universal_hysteresis",
        "selected_candidate": selected.to_dict() if selected is not None else None,
        "state_model": serialize_model(refit_state_model) if refit_state_model is not None else None,
        "switch_gate_model": selected_gate_model,
        "refit_data_end": REFIT_END if selected is not None else None,
    }
    _write_json(output_dir / "selected_recognizer.json", selected_payload)

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
    _write_json(output_dir / "input_identity.json", input_identity)

    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(
            selected,
            selected_aggregate,
            v5_aggregate,
            selected_2025,
            v5_2025,
            diagnostic,
            best_point,
        ),
        encoding="utf-8",
    )

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "candidate_cv.csv",
        "summary.json",
        "selected_recognizer.json",
        "input_identity.json",
    ]
    if (output_dir / "per_state_2025.csv").exists():
        output_names.append("per_state_2025.csv")
    if (output_dir / "transition_events_2025.csv").exists():
        output_names.append("transition_events_2025.csv")
    receipt = {
        "schema": "kline_recognizer_switch_gate_v8_execution_receipt@1.0",
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
