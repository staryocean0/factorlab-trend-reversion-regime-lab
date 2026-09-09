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
from regime_lab.kline_recognizer_hysteresis_v5 import V4_LINEAR_CONFIG
from regime_lab.kline_recognizer_optimization_v4 import fit_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_temporal_blend_v10 import (
    TemporalBlendCandidate,
    V5_POLICY,
    score_blend_period,
)
from regime_lab.kline_temporal_blend_v11 import (
    aggregate_fold_metrics,
    frozen_v11_menu,
    safety_veto_2025,
    select_v11_candidate,
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
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_TEMPORAL_BLEND_V11_PROTOCOL.md"
CHAMPION_PATH = ROOT / "experiments/kline_recognizer_champion.json"
CONTRIBUTION_PATH = ROOT / "experiments/kline_recognizer_contributions.json"
EXPECTED_CHAMPION_COMMIT = "723404633fccb0a52181d2090cadbca3114dcc67"
CHAMPION_CANDIDATE = TemporalBlendCandidate(6, 0.30)
AUX_C = 0.1


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
    out = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = "not-installed"
    return out


def _candidate_row(candidate, fold_results, aggregate, champion):
    row = {"candidate_id": candidate.candidate_id, **candidate.to_dict(), **aggregate}
    for k, v in champion.items():
        row[f"champion_{k}"] = v
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


def _best_local(rows):
    if not rows:
        return None, None
    return max(
        rows,
        key=lambda item: (
            float(item[1]["min_transition_f1"]),
            -float(item[1]["max_false_transitions_per_day"]),
            float(item[1]["min_balanced_accuracy"]),
            float(item[1]["min_macro_f1"]),
            -float(item[0].alpha),
        ),
    )


def _result_card(selected, selected_aggregate, best, best_aggregate, champion_aggregate, challenger_2025, champion_2025, veto):
    lines = [
        "# K-line recognizer temporal-blend v11 — result card",
        "",
        "V11 is a narrow local refinement of champion v10. Only blend alpha changes.",
        "",
        "## Champion before v11",
        "",
        "- version: `v10_temporal_blend`",
        f"- result commit: `{EXPECTED_CHAMPION_COMMIT}`",
        f"- min balanced accuracy: `{float(champion_aggregate['min_balanced_accuracy']):.3f}`",
        f"- min macro F1: `{float(champion_aggregate['min_macro_f1']):.3f}`",
        f"- min transition F1: `{float(champion_aggregate['min_transition_f1']):.3f}`",
        f"- max false transitions/day: `{float(champion_aggregate['max_false_transitions_per_day']):.3f}`",
        "",
        "## Pre-2025 decision",
        "",
        f"V11 promotion candidate found: **{selected is not None}**",
        "",
    ]
    if best is not None:
        lines.extend([
            "Best local v11 candidate (used for contribution analysis only if not promoted):",
            f"- candidate: `{best.candidate_id}`",
            f"- min balanced accuracy: `{float(best_aggregate['min_balanced_accuracy']):.3f}`",
            f"- min macro F1: `{float(best_aggregate['min_macro_f1']):.3f}`",
            f"- min transition F1: `{float(best_aggregate['min_transition_f1']):.3f}`",
            f"- max false transitions/day: `{float(best_aggregate['max_false_transitions_per_day']):.3f}`",
            "",
        ])
    if selected is None:
        lines.extend([
            "No v11 alpha passed the frozen champion noninferiority + material-improvement gate. V10 remains champion.",
            "",
            "Champion update eligibility: **False**",
            "",
            "Any useful local effect may still be considered for the Contribution Ledger in a separate governance action.",
        ])
    else:
        lines.extend([
            f"Selected alpha: `{selected.alpha:.2f}`",
            f"- min balanced accuracy: `{float(selected_aggregate['min_balanced_accuracy']):.3f}`",
            f"- min macro F1: `{float(selected_aggregate['min_macro_f1']):.3f}`",
            f"- min transition F1: `{float(selected_aggregate['min_transition_f1']):.3f}`",
            f"- max false transitions/day: `{float(selected_aggregate['max_false_transitions_per_day']):.3f}`",
            "",
            "## 2025 consumed-data safety diagnostic",
            "",
            "| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |",
            "|---|---|---:|---:|---:|---:|",
        ])
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v11", challenger_2025), ("v10 champion", champion_2025)):
                m = source[symbol]
                lines.append(
                    f"| {symbol} | {label} | {float(m['balanced_accuracy_4state']):.3f} | "
                    f"{float(m['macro_f1_4state']):.3f} | {float(m['transition_f1']):.3f} | "
                    f"{float(m['false_transitions_per_day']):.3f} |"
                )
        lines.extend(["", f"2025 safety veto: **{bool(veto['veto'])}**"])
        lines.extend(f"- {x}" for x in veto["failures"])
        lines.extend(["", f"Champion update eligibility: **{not bool(veto['veto'])}**"])
    lines.extend([
        "",
        "## Boundary",
        "",
        "The runner does not modify champion or contribution authority files. 2025 is already-consumed evidence, not fresh OOS.",
        "",
    ])
    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(description="Run frozen v11 local temporal-blend refinement.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_recognizer_temporal_blend_v11",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)

    for path in (PROTOCOL_PATH, CHAMPION_PATH, CONTRIBUTION_PATH):
        if not path.is_file():
            raise RuntimeError(f"v11 required authority input missing: {path}")

    champion_hash = _sha256(CHAMPION_PATH)
    contribution_hash = _sha256(CONTRIBUTION_PATH)
    registry = json.loads(CHAMPION_PATH.read_text(encoding="utf-8"))
    if registry.get("champion_version") != "v10_temporal_blend":
        raise RuntimeError("v11 is frozen against v10 champion")
    if registry.get("champion_result_commit") != EXPECTED_CHAMPION_COMMIT:
        raise RuntimeError("v11 champion result commit mismatch")
    champion_aggregate = registry["pre2025_worst_cell"]

    frames = {}
    judge_events = {}
    market_ranges = {}
    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        states = build_state_timeseries(market, config=RecognitionConfig())
        judge_frame, _, center_events = build_independent_judge_frame(states, config=RecognitionConfig())
        frames[symbol] = judge_frame
        judge_events[symbol] = center_events
        market_ranges[symbol] = {"frequency": "5m", "start": start, "end": end, "rows": int(len(judge_frame))}

    contexts = {symbol: build_temporal_context(frame, horizon=6) for symbol, frame in frames.items()}

    fold_models = {}
    for fold_name, train_end, _, _ in FOLDS:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if primary is None:
            raise RuntimeError("v11 primary model unexpectedly absent")
        temporal = fit_temporal_linear(
            frames,
            contexts,
            TemporalContextCandidate(6, AUX_C),
            start=None,
            end=train_end,
        )
        fold_models[fold_name] = {"primary": primary, "temporal": temporal}

    rows = []
    selection_rows = []
    for candidate in frozen_v11_menu():
        fold_results = {}
        for fold_name, _, val_start, val_end in FOLDS:
            bundle = fold_models[fold_name]
            results, _, _ = score_blend_period(
                frames,
                contexts,
                judge_events,
                bundle["primary"],
                bundle["temporal"],
                candidate,
                start=val_start,
                end=val_end,
            )
            fold_results[fold_name] = results
        aggregate = aggregate_fold_metrics(fold_results)
        selection_rows.append((candidate, aggregate))
        rows.append(_candidate_row(candidate, fold_results, aggregate, champion_aggregate))

    selected, selected_aggregate = select_v11_candidate(selection_rows, champion_aggregate)
    best, best_aggregate = _best_local(selection_rows)

    challenger_2025 = None
    champion_2025 = None
    veto = {"veto": False, "failures": []}
    if selected is not None:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        if primary is None:
            raise RuntimeError("v11 refit primary absent")
        temporal = fit_temporal_linear(
            frames,
            contexts,
            TemporalContextCandidate(6, AUX_C),
            start=None,
            end=REFIT_END,
        )
        challenger_2025, _, _ = score_blend_period(
            frames, contexts, judge_events, primary, temporal, selected,
            start=DIAGNOSTIC_START, end=DIAGNOSTIC_END,
        )
        champion_2025, _, _ = score_blend_period(
            frames, contexts, judge_events, primary, temporal, CHAMPION_CANDIDATE,
            start=DIAGNOSTIC_START, end=DIAGNOSTIC_END,
        )
        veto = safety_veto_2025(challenger_2025, champion_2025)

    eligible = selected is not None and not bool(veto["veto"])
    summary = {
        "status": "complete_temporal_blend_v11",
        "champion_before_run": registry,
        "candidate_count": len(rows),
        "selected_candidate": selected.to_dict() if selected else None,
        "selected_candidate_id": selected.candidate_id if selected else None,
        "selected_pre2025_aggregate": selected_aggregate,
        "best_local_candidate": best.to_dict() if best else None,
        "best_local_aggregate": best_aggregate,
        "diagnostic_2025_challenger": challenger_2025,
        "diagnostic_2025_champion": champion_2025,
        "2025_safety_veto": veto,
        "eligible_for_champion_update": eligible,
        "champion_registry_mutated_by_runner": False,
        "contribution_ledger_mutated_by_runner": False,
        "2025_used_for_candidate_selection": False,
        "2025_is_fresh_oos": False,
    }

    pd.DataFrame(rows).to_csv(output_dir / "candidate_cv.csv", index=False)
    _write_json(output_dir / "summary.json", summary)
    (output_dir / "RESULT_CARD.md").write_text(
        _result_card(selected, selected_aggregate, best, best_aggregate, champion_aggregate, challenger_2025, champion_2025, veto),
        encoding="utf-8",
    )

    if _sha256(CHAMPION_PATH) != champion_hash:
        raise RuntimeError("v11 mutated champion registry")
    if _sha256(CONTRIBUTION_PATH) != contribution_hash:
        raise RuntimeError("v11 mutated contribution ledger")

    receipt = {
        "status": "success",
        "code_commit": code_commit,
        "started_at_utc": started.isoformat(),
        "finished_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "packages": _package_versions(),
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "champion_sha256": champion_hash,
        "contribution_ledger_sha256": contribution_hash,
        "market_ranges": market_ranges,
        "outputs": {
            p.name: _sha256(p)
            for p in sorted(output_dir.iterdir())
            if p.is_file() and p.name != "execution_receipt.json"
        },
    }
    _write_json(output_dir / "execution_receipt.json", receipt)
    print(json.dumps({"status":"complete","selected":selected.candidate_id if selected else None,"eligible_for_champion_update":eligible}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
