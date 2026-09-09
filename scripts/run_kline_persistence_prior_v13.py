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
from regime_lab.kline_markov_filter_v7 import fit_markov_state_model
from regime_lab.kline_persistence_prior_v13 import (
    V10_BLEND,
    aggregate_fold_metrics,
    frozen_persistence_menu,
    safety_veto_2025,
    score_persistence_period,
    select_persistence_candidate,
)
from regime_lab.kline_recognizer_hysteresis_v5 import V4_LINEAR_CONFIG
from regime_lab.kline_recognizer_optimization_v4 import fit_model
from regime_lab.kline_state_recognition import RecognitionConfig, build_state_timeseries
from regime_lab.kline_temporal_blend_v10 import score_blend_period
from regime_lab.kline_temporal_context_v9 import TemporalContextCandidate, build_temporal_context, fit_temporal_linear
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
DIAG_START = "2025-01-01"
DIAG_END = "2025-12-31"
PROTOCOL_PATH = ROOT / "docs/research/KLINE_RECOGNIZER_PERSISTENCE_PRIOR_V13_PROTOCOL.md"
CHAMPION_PATH = ROOT / "experiments/kline_recognizer_champion.json"
CONTRIBUTION_PATH = ROOT / "experiments/kline_recognizer_contributions.json"
EXPECTED_CHAMPION_COMMIT = "723404633fccb0a52181d2090cadbca3114dcc67"
REQUIRED_CONTRIBUTION = "v7_persistence_prior_point_state_signal"
AUX_C = 0.1


def _sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def _git_head(override):
    if override:
        return override
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def _clean(x):
    if isinstance(x, dict): return {str(k): _clean(v) for k, v in x.items()}
    if isinstance(x, list): return [_clean(v) for v in x]
    if isinstance(x, tuple): return [_clean(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x): return None
    if isinstance(x, pd.Timestamp): return x.isoformat()
    return x


def _write_json(path, payload):
    path.write_text(json.dumps(_clean(payload), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _candidate_row(candidate, fold_results, aggregate, champion):
    row = {"candidate_id": candidate.candidate_id, **candidate.to_dict(), **aggregate}
    for k, v in champion.items(): row[f"champion_{k}"] = v
    for fold_name, assets in fold_results.items():
        for symbol, metrics in assets.items():
            prefix = f"{fold_name}_{symbol.replace('.', '_')}"
            for metric in ("balanced_accuracy_4state", "macro_f1_4state", "transition_precision", "transition_recall", "transition_f1", "false_transitions_per_day", "exact_accuracy_including_abstention", "online_concrete_coverage"):
                row[f"{prefix}_{metric}"] = metrics.get(metric)
    return row


def _card(selected, selected_agg, best, best_agg, champ, c25, b25, veto):
    lines = [
        "# K-line recognizer low-weight persistence-prior v13 — result card", "",
        "V13 integrates only the audited v7 persistence contribution into champion v10 as a one-step weak probability prior. No recursive Markov posterior or Markov decoder is used.", "",
        "## Champion before v13", "",
        "- version: `v10_temporal_blend`", f"- result commit: `{EXPECTED_CHAMPION_COMMIT}`",
        f"- min balanced accuracy: `{champ['min_balanced_accuracy']:.3f}`",
        f"- min macro F1: `{champ['min_macro_f1']:.3f}`",
        f"- min transition F1: `{champ['min_transition_f1']:.3f}`",
        f"- max false transitions/day: `{champ['max_false_transitions_per_day']:.3f}`", "",
        "## Pre-2025 decision", "", f"V13 promotion candidate found: **{selected is not None}**", "",
        "Best local v13 candidate:", f"- candidate: `{best.candidate_id}`", f"- rho: `{best.rho:.2f}`",
        f"- min balanced accuracy: `{best_agg['min_balanced_accuracy']:.3f}`",
        f"- min macro F1: `{best_agg['min_macro_f1']:.3f}`",
        f"- min transition F1: `{best_agg['min_transition_f1']:.3f}`",
        f"- max false transitions/day: `{best_agg['max_false_transitions_per_day']:.3f}`", ""
    ]
    if selected is None:
        lines += ["No v13 rho passed the frozen v10 noninferiority + material-improvement gate. V10 remains champion.", "", "Champion update eligibility: **False**"]
    else:
        lines += [f"Selected rho: `{selected.rho:.2f}`", "", "## 2025 consumed-data safety diagnostic", "", "| Asset | Recognizer | Balanced accuracy | Macro F1 | Transition F1 | False transitions/day |", "|---|---|---:|---:|---:|---:|"]
        for symbol in ("000852.SH", "000688.SH"):
            for label, source in (("v13", c25), ("v10 champion", b25)):
                m = source[symbol]
                lines.append(f"| {symbol} | {label} | {m['balanced_accuracy_4state']:.3f} | {m['macro_f1_4state']:.3f} | {m['transition_f1']:.3f} | {m['false_transitions_per_day']:.3f} |")
        lines += ["", f"2025 safety veto: **{bool(veto['veto'])}**", "", f"Champion update eligibility: **{not bool(veto['veto'])}**"]
    lines += ["", "## Boundary", "", "Runner cannot mutate champion/contribution authority. 2025 is consumed evidence, not fresh OOS.", ""]
    return "\n".join(lines)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--code-commit")
    p.add_argument("--output-dir", type=Path, default=ROOT / "experiments/kline_recognizer_persistence_prior_v13")
    return p.parse_args()


def main():
    args = parse_args(); started = datetime.now(timezone.utc); out = args.output_dir.resolve(); out.mkdir(parents=True, exist_ok=True)
    code_commit = _git_head(args.code_commit)
    for path in (PROTOCOL_PATH, CHAMPION_PATH, CONTRIBUTION_PATH):
        if not path.is_file(): raise RuntimeError(f"v13 authority input missing: {path}")
    champ_hash, contrib_hash = _sha(CHAMPION_PATH), _sha(CONTRIBUTION_PATH)
    registry = json.loads(CHAMPION_PATH.read_text(encoding="utf-8"))
    if registry.get("champion_version") != "v10_temporal_blend" or registry.get("champion_result_commit") != EXPECTED_CHAMPION_COMMIT:
        raise RuntimeError("v13 frozen champion pointer mismatch")
    champ = registry["pre2025_worst_cell"]
    ledger = json.loads(CONTRIBUTION_PATH.read_text(encoding="utf-8"))
    if REQUIRED_CONTRIBUTION not in {x.get("contribution_id") for x in ledger.get("contributions", [])}:
        raise RuntimeError("v13 required v7 contribution missing")

    frames, judge_events, market_ranges = {}, {}, {}
    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        states = build_state_timeseries(market, config=RecognitionConfig())
        judge, _, events = build_independent_judge_frame(states, config=RecognitionConfig())
        frames[symbol], judge_events[symbol] = judge, events
        market_ranges[symbol] = {"frequency":"5m","start":start,"end":end,"rows":len(judge)}
    contexts = {s: build_temporal_context(f, horizon=6) for s, f in frames.items()}

    fold_models = {}
    for fold_name, train_end, _, _ in FOLDS:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=train_end)
        if primary is None: raise RuntimeError("v13 primary absent")
        temporal = fit_temporal_linear(frames, contexts, TemporalContextCandidate(6, AUX_C), start=None, end=train_end)
        markov = fit_markov_state_model(frames, start=None, end=train_end)
        fold_models[fold_name] = {"primary":primary,"temporal":temporal,"markov":markov}

    rows, selection = [], []
    for cand in frozen_persistence_menu():
        fold_results = {}
        for fold_name, _, val_start, val_end in FOLDS:
            b = fold_models[fold_name]
            metrics, _, _ = score_persistence_period(frames, contexts, judge_events, b["primary"], b["temporal"], b["markov"], cand, start=val_start, end=val_end)
            fold_results[fold_name] = metrics
        agg = aggregate_fold_metrics(fold_results)
        selection.append((cand, agg)); rows.append(_candidate_row(cand, fold_results, agg, champ))

    selected, selected_agg, best, best_agg = select_persistence_candidate(selection, champ)
    c25 = b25 = None; veto = {"veto":False,"failures":[]}; model = None
    if selected is not None:
        primary = fit_model(frames, V4_LINEAR_CONFIG, start=None, end=REFIT_END)
        temporal = fit_temporal_linear(frames, contexts, TemporalContextCandidate(6, AUX_C), start=None, end=REFIT_END)
        markov = fit_markov_state_model(frames, start=None, end=REFIT_END)
        c25, _, _ = score_persistence_period(frames, contexts, judge_events, primary, temporal, markov, selected, start=DIAG_START, end=DIAG_END)
        b25, _, _ = score_blend_period(frames, contexts, judge_events, primary, temporal, V10_BLEND, start=DIAG_START, end=DIAG_END)
        veto = safety_veto_2025(c25, b25)
        model = {"candidate":selected.to_dict(),"primary_model":primary,"temporal_model":temporal,"markov_model":markov,"2025_safety_veto":veto}

    eligible = selected is not None and not bool(veto["veto"])
    summary = {"status":"complete_persistence_prior_v13","champion_before_run":registry,"source_contribution":REQUIRED_CONTRIBUTION,"candidate_count":len(rows),"selected_candidate":selected.to_dict() if selected else None,"selected_candidate_id":selected.candidate_id if selected else None,"selected_pre2025_aggregate":selected_agg,"best_local_candidate":best.to_dict(),"best_local_aggregate":best_agg,"diagnostic_2025_challenger":c25,"diagnostic_2025_champion":b25,"2025_safety_veto":veto,"eligible_for_champion_update":eligible,"champion_registry_mutated_by_runner":False,"contribution_ledger_mutated_by_runner":False,"2025_used_for_candidate_selection":False,"2025_is_fresh_oos":False}
    pd.DataFrame(rows).to_csv(out / "candidate_cv.csv", index=False); _write_json(out / "summary.json", summary)
    if model is not None: _write_json(out / "selected_recognizer.json", model)
    (out / "RESULT_CARD.md").write_text(_card(selected, selected_agg, best, best_agg, champ, c25, b25, veto), encoding="utf-8")
    if _sha(CHAMPION_PATH) != champ_hash: raise RuntimeError("v13 mutated champion")
    if _sha(CONTRIBUTION_PATH) != contrib_hash: raise RuntimeError("v13 mutated contribution ledger")
    receipt = {"status":"success","code_commit":code_commit,"started_at_utc":started.isoformat(),"finished_at_utc":datetime.now(timezone.utc).isoformat(),"python":platform.python_version(),"protocol_sha256":_sha(PROTOCOL_PATH),"champion_sha256":champ_hash,"contribution_ledger_sha256":contrib_hash,"market_ranges":market_ranges,"packages":{n:importlib.metadata.version(n) for n in ("numpy","pandas","pyarrow","scipy")},"outputs":{p.name:_sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != "execution_receipt.json"}}
    _write_json(out / "execution_receipt.json", receipt); print(json.dumps(summary, ensure_ascii=False, indent=2)); return 0


if __name__ == "__main__": raise SystemExit(main())
