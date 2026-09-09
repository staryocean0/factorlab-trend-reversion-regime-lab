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
    score_policy_period,
)
from regime_lab.kline_recognizer_optimization_v4 import fit_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_temporal_context_v9 import (
    V5_POLICY,
    aggregate_fold_metrics,
    build_temporal_context,
    fit_temporal_linear,
    frozen_temporal_menu,
    safety_veto_2025,
    score_temporal_period,
    select_temporal_candidate,
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_TEMPORAL_CONTEXT_V9_PROTOCOL.md"
CHAMPION_PATH = ROOT / "experiments/kline_recognizer_champion.json"
V5_SUMMARY_PATH = ROOT / "experiments/kline_recognizer_hysteresis_v5/summary.json"
EXPECTED_CHAMPION_COMMIT = "e4ddffd3c190ba18739587aabf73844b3daa2230"


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


def _candidate_row(candidate, fold_results, aggregate, champion):
    row: dict[str, object] = {
        "candidate_id": candidate.candidate_id,
        **candidate.to_dict(),
        **aggregate,
    }
    for key, value in champion.items():
        row[f"champion_{key}"] = value
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


def _diagnostic_table(challenger, champion):
    rows: list[dict[str, object]] = []
    for symbol in ("000852.SH", "000688.SH"):
        for role, source in (("v9_temporal", challenger), ("v5_champion", champion)):
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
    champion_aggregate,
    challenger_2025,
    champion_2025,
    veto,
) -> str:
    lines = [
        "# K-line recognizer temporal-context v9 — result card",
        "",
        "V9 changes the primary four-state classifier only. The v5 champion decoder remains fixed.",
        "",
        "## Champion before v9",
        "",
        "- version: `v5_probability_hysteresis`",
        f"- result commit: `{EXPECTED_CHAMPION_COMMIT}`",
        f"- pre-2025 min balanced accuracy: `{float(champion_aggregate['min_balanced_accuracy']):.3f}`",
        f"- pre-2025 min macro F1: `{float(champion_aggregate['min_macro_f1']):.3f}`",
        f"- pre-2025 min transition F1: `{float(champion_aggregate['min_transition_f1']):.3f}`",
        f"- pre-2025 max false transitions/day: `{float(champion_aggregate['max_false_transitions_per_day']):.3f}`",
        "",
        "## Pre-2025 challenger decision",
        "",
        f"V9 candidate passed promotion gate: **{selected is not None}**",
        "",
    ]
    if best is not None:
        lines.extend(
            [
                "Best point-noninferior v9 candidate:",
                f"- candidate: `{best.candidate_id}`",
                f"- minimum balanced accuracy: `{float(best_aggregate['min_balanced_accuracy']):.3f}`",
                f"- minimum macro F1: `{float(best_aggregate['min_macro_f1']):.3f}`",
                f"- minimum transition F1: `{float(best_aggregate['min_transition_f1']):.3f}`",
                f"- maximum false transitions/day: `{float(best_aggregate['max_false_transitions_per_day']):.3f}`",
                "",
            ]
        )
    if selected is None:
        lines.extend(
            [
                "No v9 candidate satisfied the frozen noninferiority + material-improvement gate. The champion registry must remain v5. 2025 was not used to rescue v9.",
                "",
                "Champion update eligibility: **False**",
            ]
        )
    else:
        lines.extend(
            [
                "Selected v9 challenger:",
                f"- candidate: `{selected.candidate_id}`",
                f"- horizon: `{selected.horizon}` bars",
                f"- C: `{selected.C:g}`",
                f"- minimum balanced accuracy: `{float(selected_aggregate['min_balanced_accuracy']):.3f}`",
                f"- minimum macro F1: `{float(selected_aggregate['min_macro_f1']):.3f}`",
                f"- minimum transition F1: `{float(selected_aggregate['min_transition_f1']):.3f}`",
                f"- maximum false transitions/day: `{float(selected_aggregate['max_false_transitions_per_day']):.3f}`",
                "",
                "## 2025 consumed-data safety diagnostic",
                "",
                "| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |",
                "|---|---|---:|---:|---:|---:|",
            ]
        )
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v9 temporal", challenger_2025), ("v5 champion", champion_2025)):
                m = source[symbol]
                lines.append(
                    f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                    f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_f1']):.3f} | "
                    f"{float(m['false_transitions_per_day']):.3f} |"
                )
        lines.extend(
            [
                "",
                f"2025 catastrophic-regression veto: **{bool(veto['veto'])}**",
            ]
        )
        for item in veto["failures"]:
            lines.append(f"- {item}")
        lines.extend(
            [
                "",
                f"Champion update eligibility: **{not bool(veto['veto'])}**",
            ]
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "2025 is already-consumed development evidence, not fresh OOS. The runner never edits the champion registry; registry mutation is a separate governance action after this result is reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen temporal-context v9 challenger.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_temporal_context_v9",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    if not CHAMPION_PATH.is_file() or not V5_SUMMARY_PATH.is_file():
        raise RuntimeError("v9 requires champion registry and immutable v5 summary")
    champion_registry = json.loads(CHAMPION_PATH.read_text(encoding="utf-8"))
    if champion_registry.get("champion_result_commit") != EXPECTED_CHAMPION_COMMIT:
        raise RuntimeError("v9 champion pointer is not the frozen v5 result commit")
    if champion_registry.get("champion_version") != "v5_probability_hysteresis":
        raise RuntimeError("v9 protocol frozen against v5 champion only")
    v5_summary = json.loads(V5_SUMMARY_PATH.read_text(encoding="utf-8"))
    champion_aggregate = v5_summary["cross_validation_aggregate"]

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

    contexts_by_horizon: dict[int, dict[str, pd.DataFrame]] = {}
    for horizon in (3, 6):
        contexts_by_horizon[horizon] = {
            symbol: build_temporal_context(frame, horizon=horizon)
            for symbol, frame in frames.items()
        }

    candidate_rows: list[dict[str, object]] = []
    selection_rows = []
    fold_audit: dict[str, object] = {}
    for candidate in frozen_temporal_menu():
        fold_results: dict[str, dict[str, dict[str, object]]] = {}
        model_audit: dict[str, object] = {}
        contexts = contexts_by_horizon[candidate.horizon]
        for fold_name, train_end, val_start, val_end in FOLDS:
            model = fit_temporal_linear(
                frames,
                contexts,
                candidate,
                start=None,
                end=train_end,
            )
            results, _, _ = score_temporal_period(
                frames,
                contexts,
                judge_events,
                model,
                start=val_start,
                end=val_end,
            )
            fold_results[fold_name] = results
            model_audit[fold_name] = {
                "train_end": train_end,
                "optimizer_iterations": model["optimizer_iterations"],
                "optimizer_loss": model["optimizer_loss"],
            }
        aggregate = aggregate_fold_metrics(fold_results)
        selection_rows.append((candidate, aggregate))
        candidate_rows.append(_candidate_row(candidate, fold_results, aggregate, champion_aggregate))
        fold_audit[candidate.candidate_id] = model_audit

    selected, selected_aggregate, best, best_aggregate = select_temporal_candidate(
        selection_rows, champion_aggregate
    )

    challenger_2025 = None
    champion_2025 = None
    veto = {"veto": False, "failures": []}
    diagnostic_table = pd.DataFrame()
    per_state_table = pd.DataFrame()
    transition_table = pd.DataFrame()
    selected_recognizer = None

    if selected is not None:
        contexts = contexts_by_horizon[selected.horizon]
        refit = fit_temporal_linear(
            frames,
            contexts,
            selected,
            start=None,
            end=REFIT_END,
        )
        challenger_2025, per_state, transitions = score_temporal_period(
            frames,
            contexts,
            judge_events,
            refit,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        v5_classifier = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        if v5_classifier is None:
            raise RuntimeError("v5 classifier refit unexpectedly absent")
        champion_2025, _, _ = score_policy_period(
            frames,
            judge_events,
            v5_classifier,
            V5_POLICY,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        veto = safety_veto_2025(challenger_2025, champion_2025)
        diagnostic_table = _diagnostic_table(challenger_2025, champion_2025)
        per_state_table = pd.concat(
            [table.assign(symbol=symbol) for symbol, table in per_state.items()],
            ignore_index=True,
        )
        transition_table = pd.concat(
            [table.assign(symbol=symbol) for symbol, table in transitions.items()],
            ignore_index=True,
            sort=False,
        )
        selected_recognizer = {
            "candidate": selected.to_dict(),
            "pre2025_aggregate": selected_aggregate,
            "refit_data_end": REFIT_END,
            "model": refit,
            "2025_safety_veto": veto,
            "eligible_for_champion_update": not bool(veto["veto"]),
        }

    eligible_for_champion_update = selected is not None and not bool(veto["veto"])
    summary = {
        "status": "complete_temporal_context_v9",
        "champion_before_run": champion_registry,
        "candidate_count": len(candidate_rows),
        "pre2025_selected_candidate": selected.to_dict() if selected is not None else None,
        "pre2025_selected_candidate_id": selected.candidate_id if selected is not None else None,
        "pre2025_selected_aggregate": selected_aggregate,
        "best_point_noninferior_candidate": best.to_dict() if best is not None else None,
        "best_point_noninferior_aggregate": best_aggregate,
        "champion_pre2025_aggregate": champion_aggregate,
        "diagnostic_2025_challenger": challenger_2025,
        "diagnostic_2025_champion": champion_2025,
        "2025_safety_veto": veto,
        "eligible_for_champion_update": bool(eligible_for_champion_update),
        "champion_registry_mutated_by_runner": False,
        "2025_used_for_candidate_selection": False,
        "2025_is_fresh_oos": False,
        "fold_model_audit": fold_audit,
    }

    candidate_table = pd.DataFrame(candidate_rows)
    candidate_table.to_csv(output_dir / "candidate_cv.csv", index=False)
    if not diagnostic_table.empty:
        diagnostic_table.to_csv(output_dir / "diagnostic_2025.csv", index=False)
        per_state_table.to_csv(output_dir / "per_state_2025.csv", index=False)
        transition_table.to_csv(output_dir / "transition_events_2025.csv", index=False)
    if selected_recognizer is not None:
        _write_json(output_dir / "selected_recognizer.json", selected_recognizer)
    _write_json(output_dir / "summary.json", summary)

    input_identity = {
        "code_commit": code_commit,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "champion_registry_sha256": _sha256(CHAMPION_PATH),
        "v5_summary_sha256": _sha256(V5_SUMMARY_PATH),
        "expected_champion_result_commit": EXPECTED_CHAMPION_COMMIT,
        "market_manifest_sha256": _sha256(ROOT / "data/manifest.json"),
        "market_ranges": market_ranges,
        "folds": FOLDS,
        "diagnostic_2025": [DIAGNOSTIC_START, DIAGNOSTIC_END],
        "2026_excluded": True,
    }
    _write_json(output_dir / "input_identity.json", input_identity)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(
            selected=selected,
            selected_aggregate=selected_aggregate,
            best=best,
            best_aggregate=best_aggregate,
            champion_aggregate=champion_aggregate,
            challenger_2025=challenger_2025,
            champion_2025=champion_2025,
            veto=veto,
        ),
        encoding="utf-8",
    )

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "candidate_cv.csv",
        "summary.json",
        "input_identity.json",
    ]
    for optional in (
        "diagnostic_2025.csv",
        "per_state_2025.csv",
        "transition_events_2025.csv",
        "selected_recognizer.json",
    ):
        if (output_dir / optional).is_file():
            output_names.append(optional)
    receipt = {
        "schema": "kline_recognizer_temporal_context_v9_execution_receipt@1.0",
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
