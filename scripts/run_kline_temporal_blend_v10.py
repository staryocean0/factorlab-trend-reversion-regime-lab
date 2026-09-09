from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from regime_lab.kline_independent_judge_v3 import build_independent_judge_frame
from regime_lab.kline_recognizer_hysteresis_v5 import V4_LINEAR_CONFIG, score_policy_period
from regime_lab.kline_recognizer_optimization_v4 import fit_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_temporal_blend_v10 import (
    AUXILIARY_C,
    V5_POLICY,
    aggregate_fold_metrics,
    frozen_blend_menu,
    safety_veto_2025,
    score_blend_period,
    select_blend_candidate,
)
from regime_lab.kline_temporal_context_v9 import (
    TemporalContextCandidate,
    build_temporal_context,
    fit_temporal_linear,
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_TEMPORAL_BLEND_V10_PROTOCOL.md"
CHAMPION_PATH = ROOT / "experiments/kline_recognizer_champion.json"
CONTRIBUTION_PATH = ROOT / "experiments/kline_recognizer_contributions.json"
V5_SUMMARY_PATH = ROOT / "experiments/kline_recognizer_hysteresis_v5/summary.json"
EXPECTED_CHAMPION_COMMIT = "e4ddffd3c190ba18739587aabf73844b3daa2230"
REQUIRED_CONTRIBUTIONS = {"v9_temporal_context_h3", "v9_temporal_context_h6"}


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _git_head(override: str | None) -> str:
    if override:
        return override
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


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
    row: dict[str, object] = {"candidate_id": candidate.candidate_id, **candidate.to_dict(), **aggregate}
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


def _result_card(selected, aggregate, champion_aggregate, challenger_2025, champion_2025, veto):
    lines = [
        "# K-line recognizer temporal-blend v10 — result card",
        "",
        "V10 integrates the retained v9 temporal-context contribution into the v5 champion. The v5 decoder remains unchanged.",
        "",
        "## Champion before v10",
        "",
        "- version: `v5_probability_hysteresis`",
        f"- result commit: `{EXPECTED_CHAMPION_COMMIT}`",
        f"- min balanced accuracy: `{float(champion_aggregate['min_balanced_accuracy']):.3f}`",
        f"- min macro F1: `{float(champion_aggregate['min_macro_f1']):.3f}`",
        f"- min transition F1: `{float(champion_aggregate['min_transition_f1']):.3f}`",
        f"- max false transitions/day: `{float(champion_aggregate['max_false_transitions_per_day']):.3f}`",
        "",
        "## Pre-2025 contribution-integration decision",
        "",
        f"V10 candidate passed promotion gate: **{selected is not None}**",
        "",
    ]
    if selected is None:
        lines.extend([
            "No blend candidate preserved all champion floors while delivering a frozen material improvement. V5 remains champion.",
            "",
            "Champion update eligibility: **False**",
        ])
    else:
        lines.extend([
            f"- selected: `{selected.candidate_id}`",
            f"- temporal horizon: `{selected.horizon}` bars",
            f"- blend alpha: `{selected.alpha:.2f}`",
            f"- auxiliary C: `{AUXILIARY_C}`",
            f"- min balanced accuracy: `{float(aggregate['min_balanced_accuracy']):.3f}`",
            f"- min macro F1: `{float(aggregate['min_macro_f1']):.3f}`",
            f"- min transition F1: `{float(aggregate['min_transition_f1']):.3f}`",
            f"- max false transitions/day: `{float(aggregate['max_false_transitions_per_day']):.3f}`",
            "",
            "## 2025 consumed-data safety diagnostic",
            "",
            "| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |",
            "|---|---|---:|---:|---:|---:|",
        ])
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v10 blend", challenger_2025), ("v5 champion", champion_2025)):
                m = source[symbol]
                lines.append(
                    f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                    f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_f1']):.3f} | "
                    f"{float(m['false_transitions_per_day']):.3f} |"
                )
        lines.extend(["", f"2025 safety veto: **{bool(veto['veto'])}**"])
        lines.extend(f"- {item}" for item in veto["failures"])
        lines.extend(["", f"Champion update eligibility: **{not bool(veto['veto'])}**"])
    lines.extend([
        "",
        "## Governance boundary",
        "",
        "The runner is forbidden from editing the champion registry. A champion change, if eligible, is a separate reviewed governance action.",
        "2025 is already-consumed evidence and is not a fresh-OOS claim.",
        "",
    ])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen v10 temporal contribution blend.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_temporal_blend_v10",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    for required in (PROTOCOL_PATH, CHAMPION_PATH, CONTRIBUTION_PATH, V5_SUMMARY_PATH):
        if not required.is_file():
            raise RuntimeError(f"required v10 authority input missing: {required}")

    champion_hash_before = _sha256(CHAMPION_PATH)
    contribution_hash_before = _sha256(CONTRIBUTION_PATH)
    champion_registry = json.loads(CHAMPION_PATH.read_text(encoding="utf-8"))
    if champion_registry.get("champion_result_commit") != EXPECTED_CHAMPION_COMMIT:
        raise RuntimeError("v10 protocol is frozen against the v5 champion commit")
    if champion_registry.get("champion_version") != "v5_probability_hysteresis":
        raise RuntimeError("v10 champion is not v5")

    contribution_ledger = json.loads(CONTRIBUTION_PATH.read_text(encoding="utf-8"))
    ids = {row.get("contribution_id") for row in contribution_ledger.get("contributions", [])}
    if not REQUIRED_CONTRIBUTIONS.issubset(ids):
        raise RuntimeError("required retained v9 temporal contributions are missing")

    champion_aggregate = json.loads(V5_SUMMARY_PATH.read_text(encoding="utf-8"))["cross_validation_aggregate"]

    frames: dict[str, pd.DataFrame] = {}
    judge_events: dict[str, pd.DataFrame] = {}
    market_ranges: dict[str, object] = {}
    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        states = build_state_timeseries(market, config=RecognitionConfig())
        judge_frame, _, center_events = build_independent_judge_frame(states, config=RecognitionConfig())
        frames[symbol] = judge_frame
        judge_events[symbol] = center_events
        market_ranges[symbol] = {"frequency": "5m", "start": start, "end": end, "rows": int(len(judge_frame))}

    contexts = {
        horizon: {symbol: build_temporal_context(frame, horizon=horizon) for symbol, frame in frames.items()}
        for horizon in (3, 6)
    }

    # Fit each head once per fold; alpha candidates reuse the same fitted heads.
    fold_models: dict[str, dict[str, object]] = {}
    for fold_name, train_end, _, _ in FOLDS:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if primary is None:
            raise RuntimeError("v10 primary v5 model unexpectedly absent")
        temporal_models = {}
        for horizon in (3, 6):
            temporal_models[horizon] = fit_temporal_linear(
                frames,
                contexts[horizon],
                TemporalContextCandidate(horizon, AUXILIARY_C),
                start=None,
                end=train_end,
            )
        fold_models[fold_name] = {"primary": primary, "temporal": temporal_models, "train_end": train_end}

    rows = []
    selection_rows = []
    all_fold_results: dict[str, object] = {}
    for candidate in frozen_blend_menu():
        fold_results = {}
        for fold_name, _, val_start, val_end in FOLDS:
            bundle = fold_models[fold_name]
            results, _, _ = score_blend_period(
                frames,
                contexts[candidate.horizon],
                judge_events,
                bundle["primary"],
                bundle["temporal"][candidate.horizon],
                candidate,
                start=val_start,
                end=val_end,
            )
            fold_results[fold_name] = results
        aggregate = aggregate_fold_metrics(fold_results)
        selection_rows.append((candidate, aggregate))
        rows.append(_candidate_row(candidate, fold_results, aggregate, champion_aggregate))
        all_fold_results[candidate.candidate_id] = {"aggregate": aggregate, "folds": fold_results}

    selected, selected_aggregate = select_blend_candidate(selection_rows, champion_aggregate)

    challenger_2025 = None
    champion_2025 = None
    veto = {"veto": False, "failures": []}
    selected_model = None

    if selected is not None:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        if primary is None:
            raise RuntimeError("v10 refit primary model unexpectedly absent")
        temporal = fit_temporal_linear(
            frames,
            contexts[selected.horizon],
            TemporalContextCandidate(selected.horizon, AUXILIARY_C),
            start=None,
            end=REFIT_END,
        )
        challenger_2025, _, _ = score_blend_period(
            frames,
            contexts[selected.horizon],
            judge_events,
            primary,
            temporal,
            selected,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        champion_2025, _, _ = score_policy_period(
            frames,
            judge_events,
            primary,
            V5_POLICY,
            start=DIAGNOSTIC_START,
            end=DIAGNOSTIC_END,
        )
        veto = safety_veto_2025(challenger_2025, champion_2025)
        selected_model = {
            "candidate": selected.to_dict(),
            "primary_model": primary,
            "temporal_model": temporal,
            "refit_data_end": REFIT_END,
            "2025_safety_veto": veto,
        }

    eligible_for_champion_update = selected is not None and not bool(veto["veto"])

    summary = {
        "status": "complete_temporal_blend_v10",
        "champion_before_run": champion_registry,
        "contribution_source_ids": sorted(REQUIRED_CONTRIBUTIONS),
        "candidate_count": len(rows),
        "selected_candidate": selected.to_dict() if selected else None,
        "selected_candidate_id": selected.candidate_id if selected else None,
        "selected_pre2025_aggregate": selected_aggregate,
        "champion_pre2025_aggregate": champion_aggregate,
        "diagnostic_2025_challenger": challenger_2025,
        "diagnostic_2025_champion": champion_2025,
        "2025_safety_veto": veto,
        "eligible_for_champion_update": eligible_for_champion_update,
        "champion_registry_mutated_by_runner": False,
        "2025_used_for_candidate_selection": False,
        "2025_is_fresh_oos": False,
    }

    pd.DataFrame(rows).to_csv(output_dir / "candidate_cv.csv", index=False)
    _write_json(output_dir / "summary.json", summary)
    if selected_model is not None:
        _write_json(output_dir / "selected_recognizer.json", selected_model)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(selected, selected_aggregate, champion_aggregate, challenger_2025, champion_2025, veto),
        encoding="utf-8",
    )

    # Fail closed if research execution touched either authority file.
    if _sha256(CHAMPION_PATH) != champion_hash_before:
        raise RuntimeError("v10 runner mutated champion registry")
    if _sha256(CONTRIBUTION_PATH) != contribution_hash_before:
        raise RuntimeError("v10 runner mutated contribution ledger")

    finished = datetime.now(timezone.utc)
    receipt = {
        "status": "success",
        "code_commit": code_commit,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "python": platform.python_version(),
        "packages": _package_versions(),
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "champion_sha256": champion_hash_before,
        "contribution_ledger_sha256": contribution_hash_before,
        "market_ranges": market_ranges,
        "outputs": {
            p.name: _sha256(p)
            for p in sorted(output_dir.iterdir())
            if p.is_file() and p.name != "execution_receipt.json"
        },
    }
    _write_json(output_dir / "execution_receipt.json", receipt)
    print(json.dumps({
        "status": "complete",
        "selected": selected.candidate_id if selected else None,
        "eligible_for_champion_update": eligible_for_champion_update,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
