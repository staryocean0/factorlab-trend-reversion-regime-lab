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

from regime_lab.kline_state_recognition import (
    ALL_STATES,
    CONCRETE_STATES,
    RecognitionConfig,
    assess_capability_level,
    build_state_timeseries,
    score_recognition,
)
from regime_lab.market_data import ROOT, load_market_data

SYMBOL_RANGES = {
    "000852.SH": ("2015-01-05", "2025-12-31"),
    "000688.SH": ("2020-07-23", "2025-12-31"),
}
PROTOCOL_PATH = ROOT / "docs/research/KLINE_STATE_RECOGNITION_V1_PROTOCOL.md"


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _git_head(root: Path, override: str | None) -> str:
    if override:
        return override
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError("unable to resolve code commit; pass --code-commit") from exc
    return result.stdout.strip()


def _package_versions() -> dict[str, str]:
    versions: dict[str, str] = {}
    for name in ("numpy", "pandas", "pyarrow", "scipy"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "not-installed"
    return versions


def _clean_json_value(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _clean_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [_clean_json_value(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(_clean_json_value(payload), ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _confusion_long(symbol: str, confusion: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for truth in CONCRETE_STATES:
        for prediction in ALL_STATES:
            rows.append(
                {
                    "symbol": symbol,
                    "oracle_state": truth,
                    "predicted_state": prediction,
                    "count": int(confusion.at[truth, prediction]) if not confusion.empty else 0,
                }
            )
    return pd.DataFrame(rows)


def _year_stability(yearly: pd.DataFrame) -> dict[str, object]:
    if yearly.empty:
        return {
            "eligible_year_count": 0,
            "eligible_year_balanced_accuracy_median": math.nan,
            "eligible_year_balanced_accuracy_min": math.nan,
        }
    eligible = yearly.loc[
        (yearly["n_scored"] >= 1000)
        & (yearly["min_state_support"] >= 25)
        & yearly["balanced_accuracy_4state"].notna()
    ]
    return {
        "eligible_year_count": int(len(eligible)),
        "eligible_year_balanced_accuracy_median": float(eligible["balanced_accuracy_4state"].median()) if not eligible.empty else math.nan,
        "eligible_year_balanced_accuracy_min": float(eligible["balanced_accuracy_4state"].min()) if not eligible.empty else math.nan,
    }


def _result_card(level: dict[str, object], assets: dict[str, dict[str, object]]) -> str:
    lines = [
        "# K-line state recognition v1 — result card",
        "",
        f"Primary project capability: **{level.get('level', 'inconclusive')}**",
        "",
        "This score measures historical K-line state recognition against the frozen centered visual-reference judge. It is not a trading-profit score and not fresh OOS validation.",
        "",
        "## Asset scorecard",
        "",
        "| Asset | Balanced accuracy | Macro F1 | Concrete coverage | Transition F1 | Exact accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for symbol in ("000852.SH", "000688.SH"):
        result = assets[symbol]
        lines.append(
            "| {symbol} | {bal:.3f} | {macro:.3f} | {coverage:.3f} | {transition:.3f} | {exact:.3f} |".format(
                symbol=symbol,
                bal=float(result.get("balanced_accuracy_4state", math.nan)),
                macro=float(result.get("macro_f1_4state", math.nan)),
                coverage=float(result.get("online_concrete_coverage", math.nan)),
                transition=float(result.get("transition_f1", math.nan)),
                exact=float(result.get("exact_accuracy_including_abstention", math.nan)),
            )
        )
    lines.extend(
        [
            "",
            "## Maturity adjudication",
            "",
            f"Reason: {level.get('reason', '')}",
            "",
        ]
    )
    failures = list(level.get("failures", [])) if isinstance(level.get("failures", []), list) else []
    if failures:
        lines.append("Failed higher-level gates:")
        for item in failures:
            lines.append(f"- {item}")
        lines.append("")
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "- Level 2: pipeline exists but recognition is not yet reliably useful by the frozen gates.",
            "- Level 3: useful historical chart-state recognition on both indices.",
            "- Level 4: strong and reasonably stable historical recognition on both indices.",
            "- Level 5 cannot be awarded by this consumed-history study; it requires fresh or independently annotated evidence.",
            "",
            "No production routing or live-trading authority is granted.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run frozen K-line state recognition v1 scoring.")
    parser.add_argument("--code-commit")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/kline_state_recognition_v1",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    config = RecognitionConfig()
    code_commit = _git_head(ROOT, args.code_commit)

    state_parts: list[pd.DataFrame] = []
    confusion_parts: list[pd.DataFrame] = []
    per_state_parts: list[pd.DataFrame] = []
    yearly_parts: list[pd.DataFrame] = []
    transition_parts: list[pd.DataFrame] = []
    asset_results: dict[str, dict[str, object]] = {}
    input_ranges: dict[str, dict[str, object]] = {}

    for symbol, (start, end) in SYMBOL_RANGES.items():
        market = load_market_data(symbol, "5m", start, end)
        if market.empty:
            raise RuntimeError(f"verified 5m market data is empty for {symbol}")
        states = build_state_timeseries(market, config=config)
        if states.empty:
            raise RuntimeError(f"state timeseries is empty for {symbol}")
        summary, confusion, per_state, yearly, transitions = score_recognition(states, config=config)
        if not summary:
            raise RuntimeError(f"no concrete oracle scoring rows for {symbol}")

        min_support = int(per_state["support"].min()) if not per_state.empty else 0
        stability = _year_stability(yearly)
        asset_summary = {
            **summary,
            "min_state_support": min_support,
            **stability,
        }
        asset_results[symbol] = asset_summary
        input_ranges[symbol] = {
            "frequency": "5m",
            "start": start,
            "end": end,
            "market_rows": int(len(market)),
            "state_rows": int(len(states)),
            "recognition_eligible_rows": int(states["recognition_eligible"].sum()),
        }

        export_columns = [
            "symbol",
            "trading_day",
            "market_time_shanghai",
            "bar_ordinal_day",
            "recognition_eligible",
            "online_state",
            "oracle_state",
            "volatility_rank_prior480",
            "abs_return_rank_prior480",
            "signed_efficiency_6",
            "signed_efficiency_12",
            "bdci_12",
            "dii_12",
            "realized_volatility_12",
            "body_to_range_ratio_6",
            "wick_imbalance_6",
            "close_location_value_6",
            "oracle_signed_efficiency_12",
            "oracle_bdci_12",
            "oracle_dii_12",
            "oracle_realized_volatility_12",
            "oracle_volatility_rank_prior480",
            "oracle_abs_return_rank_prior480",
        ]
        state_parts.append(states[export_columns].copy())
        confusion_parts.append(_confusion_long(symbol, confusion))
        per_state_parts.append(per_state.assign(symbol=symbol))
        yearly_parts.append(yearly.assign(symbol=symbol))
        if not transitions.empty:
            transition_parts.append(transitions.assign(symbol=symbol))

    level = assess_capability_level(asset_results)
    state_timeseries = pd.concat(state_parts, ignore_index=True)
    confusion_matrix = pd.concat(confusion_parts, ignore_index=True)
    per_state_metrics = pd.concat(per_state_parts, ignore_index=True)
    yearly_metrics = pd.concat(yearly_parts, ignore_index=True)
    transition_events = pd.concat(transition_parts, ignore_index=True) if transition_parts else pd.DataFrame()

    manifest_path = ROOT / "data/manifest.json"
    protocol_sha = _sha256(PROTOCOL_PATH)
    feature_contract = {
        "schema": "kline_state_recognition_v1_feature_contract@1.0",
        "clock": "5m",
        "online_prefix_only": True,
        "states": list(ALL_STATES),
        "concrete_states": list(CONCRETE_STATES),
        "short_window_bars": config.short_window,
        "primary_window_bars": config.primary_window,
        "reference_history_finite_values": config.reference_history,
        "oracle_radius_bars": config.oracle_radius,
        "recognition_eligibility_required": True,
        "thresholds": {
            "bdci_trend": config.bdci_trend_threshold,
            "bdci_range": config.bdci_range_threshold,
            "trend_efficiency": config.trend_efficiency_threshold,
            "range_efficiency": config.range_efficiency_threshold,
            "dii_trend_abs": config.dii_trend_threshold,
            "shock_vol_rank": config.shock_vol_rank,
            "shock_abs_return_rank": config.shock_abs_return_rank,
        },
        "transition_confirm_bars": config.transition_confirm_bars,
        "transition_tolerance_bars": config.transition_tolerance_bars,
        "forbidden_online_inputs": [
            "future_return",
            "forward_return",
            "pnl",
            "strategy_result",
            "oracle_state",
            "oracle_centered_features",
            "2026_data",
            "UK_alert",
        ],
    }
    input_identity = {
        "code_commit": code_commit,
        "protocol_path": str(PROTOCOL_PATH),
        "protocol_sha256": protocol_sha,
        "market_manifest_path": str(manifest_path),
        "market_manifest_sha256": _sha256(manifest_path),
        "market_ranges": input_ranges,
        "data_role": "consumed_development_material",
        "2026_excluded": True,
    }
    summary_payload = {
        "status": "complete_historical_recognition_score",
        "capability": level,
        "assets": asset_results,
        "level_5_available_in_v1": False,
        "primary_claim_boundary": "K-line state recognition only; not profitability or production routing",
    }

    state_timeseries.to_csv(output_dir / "state_timeseries.csv", index=False)
    transition_events.to_csv(output_dir / "transition_events.csv", index=False)
    confusion_matrix.to_csv(output_dir / "confusion_matrix.csv", index=False)
    per_state_metrics.to_csv(output_dir / "per_state_metrics.csv", index=False)
    yearly_metrics.to_csv(output_dir / "yearly_metrics.csv", index=False)
    _write_json(output_dir / "summary.json", summary_payload)
    _write_json(output_dir / "input_identity.json", input_identity)
    _write_json(output_dir / "feature_contract.json", feature_contract)
    (output_dir / "RESULT_CARD.md").write_text(_result_card(level, asset_results), encoding="utf-8")

    finished = datetime.now(timezone.utc)
    output_names = [
        "RESULT_CARD.md",
        "summary.json",
        "input_identity.json",
        "feature_contract.json",
        "state_timeseries.csv",
        "transition_events.csv",
        "confusion_matrix.csv",
        "per_state_metrics.csv",
        "yearly_metrics.csv",
    ]
    receipt = {
        "schema": "kline_state_recognition_v1_execution_receipt@1.0",
        "code_commit": code_commit,
        "protocol_sha256": protocol_sha,
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

    print(json.dumps(_clean_json_value(summary_payload), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())