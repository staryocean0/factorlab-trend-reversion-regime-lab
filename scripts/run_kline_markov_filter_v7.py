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
from regime_lab.kline_markov_filter_v7 import (
    aggregate_fold_metrics,
    diagnostic_success,
    fit_markov_state_model,
    frozen_markov_menu,
    score_markov_period_from_probabilities,
    select_markov_candidate,
)
from regime_lab.kline_recognizer_hysteresis_v5 import (
    HysteresisPolicy,
    V4_LINEAR_CONFIG,
    linear_probabilities,
    score_policy_period,
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_MARKOV_FILTER_V7_PROTOCOL.md"
V5_SUMMARY_PATH = ROOT / "experiments/kline_recognizer_hysteresis_v5/summary.json"
V5_RESULT_COMMIT = "e4ddffd3c190ba18739587aabf73844b3daa2230"
V5_POLICY = HysteresisPolicy(0.05, 0.45, 4)


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


def _candidate_row(candidate, fold_results, aggregate, baseline_aggregate):
    row: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        "eta": candidate.eta,
        "beta": candidate.beta,
        **aggregate,
        "v5_min_transition_f1": baseline_aggregate["min_transition_f1"],
        "v5_max_false_transitions_per_day": baseline_aggregate["max_false_transitions_per_day"],
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


def _diagnostic_table(selected, baseline):
    rows: list[dict[str, object]] = []
    for symbol in ("000852.SH", "000688.SH"):
        for role, source in (("v7_markov", selected), ("v5_hysteresis", baseline)):
            row = {"symbol": symbol, "role": role}
            row.update(source[symbol])
            rows.append(row)
    return pd.DataFrame(rows)


def _result_card(
    *,
    selected,
    selected_aggregate,
    best,
    best_aggregate,
    baseline_aggregate,
    diagnostic,
    baseline_2025,
    diagnostic_adjudication,
) -> str:
    promoted = selected is not None
    lines = [
        "# K-line recognizer Markov filter v7 — result card",
        "",
        "V7 modifies only recognizer A's internal causal state memory. Classifier, features and frozen benchmark are unchanged.",
        "",
        "## Pre-2025 promotion decision",
        "",
        f"Markov promoted over v5: **{promoted}**",
        "",
        "V5 frozen rolling-CV baseline:",
        f"- minimum transition F1: `{float(baseline_aggregate['min_transition_f1']):.3f}`",
        f"- maximum false transitions/day: `{float(baseline_aggregate['max_false_transitions_per_day']):.3f}`",
        f"- minimum balanced accuracy: `{float(baseline_aggregate['min_balanced_accuracy']):.3f}`",
        f"- minimum macro F1: `{float(baseline_aggregate['min_macro_f1']):.3f}`",
        "",
    ]
    if best is not None:
        lines.extend(
            [
                "Best point-eligible Markov candidate before promotion gate:",
                f"- candidate: `{best.candidate_id}`",
                f"- eta: `{best.eta:g}`; beta: `{best.beta:g}`",
                f"- minimum transition F1: `{float(best_aggregate['min_transition_f1']):.3f}`",
                f"- maximum false transitions/day: `{float(best_aggregate['max_false_transitions_per_day']):.3f}`",
                f"- minimum balanced accuracy: `{float(best_aggregate['min_balanced_accuracy']):.3f}`",
                f"- minimum macro F1: `{float(best_aggregate['min_macro_f1']):.3f}`",
                "",
            ]
        )
    if selected is not None:
        lines.extend(
            [
                "Promoted Markov recognizer:",
                f"- candidate: `{selected.candidate_id}`",
                f"- eta: `{selected.eta:g}`; beta: `{selected.beta:g}`",
                f"- minimum transition F1: `{float(selected_aggregate['min_transition_f1']):.3f}`",
                f"- maximum false transitions/day: `{float(selected_aggregate['max_false_transitions_per_day']):.3f}`",
                f"- minimum balanced accuracy: `{float(selected_aggregate['min_balanced_accuracy']):.3f}`",
                f"- minimum macro F1: `{float(selected_aggregate['min_macro_f1']):.3f}`",
                "",
                "## 2025 consumed-data diagnostic",
                "",
                "| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition precision | Transition recall | Transition F1 | False transitions/day |",
                "|---|---|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v7 Markov", diagnostic), ("v5 hysteresis", baseline_2025)):
                m = source[symbol]
                lines.append(
                    f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                    f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_precision']):.3f} | "
                    f"{float(m['transition_recall']):.3f} | {float(m['transition_f1']):.3f} | "
                    f"{float(m['false_transitions_per_day']):.3f} |"
                )
        lines.extend(["", "2025 diagnostic adjudication:", f"- **{diagnostic_adjudication['status']}**", ""])
        if diagnostic_adjudication["failures"]:
            lines.extend(f"- {item}" for item in diagnostic_adjudication["failures"])
            lines.append("")
        if diagnostic_adjudication["strong_target_passed"]:
            lines.append("The stronger target also passed on both assets.")
        else:
            lines.append("Stronger target not yet passed:")
            lines.extend(f"- {item}" for item in diagnostic_adjudication["strong_target_failures"])
    else:
        lines.extend(
            [
                "No Markov candidate satisfied the preregistered pre-2025 promotion gate. V5 remains the active recognizer and no Markov 2025 diagnostic was used for model selection or rescue.",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "2025 was already consumed by earlier development and is diagnostic only. This is chart-state recognition research, not trading profitability or fresh OOS performance.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen v7 causal Markov persistence-filter optimization.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_markov_filter_v7",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    if not V5_SUMMARY_PATH.is_file():
        raise RuntimeError("immutable v5 summary is required for v7 promotion gate")
    v5_summary = json.loads(V5_SUMMARY_PATH.read_text(encoding="utf-8"))
    baseline_aggregate = v5_summary["cross_validation_aggregate"]

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

    fold_probabilities: dict[str, dict[str, pd.DataFrame]] = {}
    fold_markov_models: dict[str, dict[str, object]] = {}
    for fold_name, train_end, _, _ in FOLDS:
        classifier = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if classifier is None:
            raise RuntimeError("locked v7 linear classifier unexpectedly absent")
        fold_probabilities[fold_name] = {
            symbol: linear_probabilities(frame, classifier) for symbol, frame in frames.items()
        }
        fold_markov_models[fold_name] = fit_markov_state_model(
            frames, start=None, end=train_end
        )

    candidate_rows: list[dict[str, object]] = []
    selection_rows = []
    all_fold_results: dict[str, dict[str, object]] = {}
    for candidate in frozen_markov_menu():
        fold_results: dict[str, dict[str, dict[str, object]]] = {}
        for fold_name, _, validation_start, validation_end in FOLDS:
            results, _, _ = score_markov_period_from_probabilities(
                frames,
                fold_probabilities[fold_name],
                judge_events,
                fold_markov_models[fold_name],
                candidate,
                start=validation_start,
                end=validation_end,
            )
            fold_results[fold_name] = results
        aggregate = aggregate_fold_metrics(fold_results)
        candidate_rows.append(_candidate_row(candidate, fold_results, aggregate, baseline_aggregate))
        selection_rows.append((candidate, aggregate))
        all_fold_results[candidate.candidate_id] = {
            "aggregate": aggregate,
            "folds": fold_results,
        }

    selected, selected_aggregate, best, best_aggregate = select_markov_candidate(
        selection_rows, baseline_aggregate
    )

    selected_2025 = None
    baseline_2025 = None
    diagnostic_adjudication = None
    per_state_selected: dict[str, pd.DataFrame] = {}
    transitions_selected: dict[str, pd.DataFrame] = {}
    selected_recognizer: dict[str, object] = {
        "active_baseline": "v5_hysteresis",
        "markov_promoted": False,
        "best_pre2025_markov": best.to_dict() if best is not None else None,
        "best_pre2025_markov_aggregate": best_aggregate,
    }

    transition_models = {
        fold_name: model for fold_name, model in fold_markov_models.items()
    }

    if selected is not None:
        refit_classifier = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        if refit_classifier is None:
            raise RuntimeError("v7 refit classifier unexpectedly absent")
        refit_probabilities = {
            symbol: linear_probabilities(frame, refit_classifier) for symbol, frame in frames.items()
        }
        refit_markov = fit_markov_state_model(frames, start=None, end=REFIT_END)
        transition_models["refit_through_2024"] = refit_markov

        selected_2025, per_state_selected, transitions_selected = score_markov_period_from_probabilities(
            frames,
            refit_probabilities,
            judge_events,
            refit_markov,
            selected,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        baseline_2025, _, _ = score_policy_period(
            frames,
            judge_events,
            refit_classifier,
            V5_POLICY,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        diagnostic_adjudication = diagnostic_success(selected_2025, baseline_2025)
        selected_recognizer = {
            "active_baseline": "v7_markov",
            "markov_promoted": True,
            "candidate": selected.to_dict(),
            "pre2025_aggregate": selected_aggregate,
            "classifier": serialize_model(refit_classifier),
            "markov_model": refit_markov,
            "refit_data_end": REFIT_END,
            "diagnostic_adjudication": diagnostic_adjudication,
        }

    summary = {
        "status": "complete_markov_filter_v7_tuning",
        "markov_promoted_pre2025": selected is not None,
        "selected_candidate": selected.to_dict() if selected is not None else None,
        "selected_candidate_id": selected.candidate_id if selected is not None else None,
        "selected_pre2025_aggregate": selected_aggregate,
        "best_point_eligible_candidate": best.to_dict() if best is not None else None,
        "best_point_eligible_candidate_id": best.candidate_id if best is not None else None,
        "best_point_eligible_aggregate": best_aggregate,
        "v5_pre2025_baseline_aggregate": baseline_aggregate,
        "diagnostic_2025_selected": selected_2025,
        "diagnostic_2025_v5": baseline_2025,
        "diagnostic_adjudication": diagnostic_adjudication,
        "candidate_count": len(candidate_rows),
        "2025_used_for_selection": False,
        "2025_is_fresh_oos": False,
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

    pd.DataFrame(candidate_rows).to_csv(output_dir / "candidate_cv.csv", index=False)
    if selected_2025 is not None and baseline_2025 is not None:
        _diagnostic_table(selected_2025, baseline_2025).to_csv(
            output_dir / "diagnostic_2025.csv", index=False
        )
        pd.concat(
            [table.assign(symbol=symbol) for symbol, table in per_state_selected.items()],
            ignore_index=True,
        ).to_csv(output_dir / "per_state_2025.csv", index=False)
        pd.concat(
            [table.assign(symbol=symbol) for symbol, table in transitions_selected.items()],
            ignore_index=True,
            sort=False,
        ).to_csv(output_dir / "transition_events_2025.csv", index=False)
    else:
        pd.DataFrame().to_csv(output_dir / "diagnostic_2025.csv", index=False)
        pd.DataFrame().to_csv(output_dir / "per_state_2025.csv", index=False)
        pd.DataFrame().to_csv(output_dir / "transition_events_2025.csv", index=False)

    _write_json(output_dir / "transition_models.json", transition_models)
    _write_json(output_dir / "selected_recognizer.json", selected_recognizer)
    _write_json(output_dir / "summary.json", summary)
    _write_json(output_dir / "input_identity.json", input_identity)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(
            selected=selected,
            selected_aggregate=selected_aggregate,
            best=best,
            best_aggregate=best_aggregate,
            baseline_aggregate=baseline_aggregate,
            diagnostic=selected_2025,
            baseline_2025=baseline_2025,
            diagnostic_adjudication=diagnostic_adjudication,
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
        "transition_models.json",
        "selected_recognizer.json",
        "summary.json",
        "input_identity.json",
    ]
    receipt = {
        "schema": "kline_recognizer_markov_filter_v7_execution_receipt@1.0",
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
