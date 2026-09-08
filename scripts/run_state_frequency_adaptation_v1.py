from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from regime_lab.market_data import ROOT, load_market_data
from regime_lab.state_frequency_adaptation import (
    ALLOWED_STATES,
    HORIZONS,
    StatePoolError,
    build_frequency_observations,
    continuous_session_segment,
    strict_quality_mask,
    summarize_observations,
    validate_state_pool,
)
from regime_lab.state_frequency_inference import (
    cost_survival_summary,
    day_block_break_even_uncertainty,
    frequency_contrasts,
    seasonality_matched_summary,
)

SYMBOLS = ("000852.SH", "000688.SH")
FAMILIES = ("trend", "reversion")
FORBIDDEN_STATE_SURFACE_TOKENS = (
    "future",
    "forward",
    "lead_",
    "target",
    "outcome",
    "pnl",
    "gross_edge",
    "net_edge",
    "horizon_return",
    "tested_return",
)


def _sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _read_state_pool(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise StatePoolError("state pool must be CSV or Parquet")


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
    names = ["numpy", "pandas", "pyarrow", "scipy"]
    out: dict[str, str] = {}
    for name in names:
        try:
            out[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            out[name] = "not-installed"
    return out


def _records(frame: pd.DataFrame) -> list[dict[str, object]]:
    if frame.empty:
        return []
    clean = frame.astype(object).where(pd.notna(frame), None)
    return clean.to_dict(orient="records")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _state_surface_audit(raw: pd.DataFrame, validated: pd.DataFrame) -> dict[str, object]:
    lower_columns = {column: str(column).lower() for column in raw.columns}
    suspicious = sorted(
        column
        for column, lowered in lower_columns.items()
        if any(token in lowered for token in FORBIDDEN_STATE_SURFACE_TOKENS)
    )
    if suspicious:
        raise StatePoolError(
            f"state pool contains forbidden future/tested-outcome surface columns: {suspicious}"
        )

    symbols = sorted(validated["symbol"].dropna().astype(str).unique())
    missing_symbols = sorted(set(SYMBOLS) - set(symbols))
    if missing_symbols:
        raise StatePoolError(f"state pool missing frozen assets: {missing_symbols}")

    timezone_names = sorted(
        {
            str(getattr(validated[column].dt, "tz", None))
            for column in ("market_time_shanghai", "state_available_at")
        }
    )
    if timezone_names != ["Asia/Shanghai"]:
        raise StatePoolError(f"unexpected timezone identity: {timezone_names}")

    lag_seconds = (
        validated["market_time_shanghai"] - validated["state_available_at"]
    ).dt.total_seconds()
    return {
        "rows": int(len(validated)),
        "symbols": symbols,
        "label_counts": {
            str(key): int(value)
            for key, value in validated["state"].astype(str).value_counts(dropna=False).items()
        },
        "primary_label_rows": int(validated["state"].isin(ALLOWED_STATES).sum()),
        "non_primary_label_rows": int((~validated["state"].isin(ALLOWED_STATES)).sum()),
        "duplicate_symbol_timestamp_rows": int(
            validated.duplicated(["symbol", "market_time_shanghai"], keep=False).sum()
        ),
        "future_availability_rows": int(
            (validated["state_available_at"] > validated["market_time_shanghai"]).sum()
        ),
        "rows_2026_or_later": int((validated["market_time_shanghai"].dt.year >= 2026).sum()),
        "timezone": "Asia/Shanghai",
        "min_availability_lag_seconds": float(lag_seconds.min()),
        "max_availability_lag_seconds": float(lag_seconds.max()),
        "extra_columns": sorted(
            set(raw.columns)
            - {"symbol", "market_time_shanghai", "state", "state_available_at"}
        ),
        "forbidden_surface_columns": suspicious,
    }


def _boundary_audit(market: pd.DataFrame) -> dict[str, int]:
    frame = market.loc[strict_quality_mask(market)].copy()
    frame["session_segment"] = continuous_session_segment(frame["market_time_shanghai"])
    frame = frame.loc[frame["session_segment"].notna()].copy()
    out: dict[str, int] = {}
    for horizon in HORIZONS:
        excluded = 0
        delta = pd.Timedelta(minutes=int(horizon))
        for _, group in frame.groupby(["trading_day", "session_segment"], sort=False):
            times = set(group["market_time_shanghai"])
            for value in group["market_time_shanghai"]:
                if value - delta not in times or value + delta not in times:
                    excluded += 1
        out[str(horizon)] = int(excluded)
    return out


def _result_card(
    observations: pd.DataFrame,
    raw_curve: pd.DataFrame,
    matched_curve: pd.DataFrame,
    uncertainty: pd.DataFrame,
    state_sha256: str,
    source_revision: str,
) -> str:
    lines = [
        "# State-frequency adaptation v1 — replay result card",
        "",
        "Status: empirical replay completed by frozen harness; primary adjudication remains a separate frozen-protocol review step.",
        "",
        "## Input gate",
        "",
        f"- state-pool SHA256: `{state_sha256}`",
        f"- state-generation source revision: `{source_revision}`",
        "- point-in-time state validation: PASS",
        "- 2026 exclusion: PASS",
        "- UK dependency: none in runner",
        "",
        "## Replay coverage",
        "",
        f"- observation rows across fixed families/horizons: `{len(observations)}`",
        f"- raw curve rows: `{len(raw_curve)}`",
        f"- seasonality-matched curve rows: `{len(matched_curve)}`",
        f"- uncertainty rows: `{len(uncertainty)}`",
        "",
        "## Primary adjudication",
        "",
        "`PENDING_FROZEN_PROTOCOL_REVIEW`",
        "",
        "This placeholder is intentionally not one of the five scientific adjudications. "
        "The replay is not protocol-complete until the thread owner reads the frozen tables and "
        "replaces it with exactly one allowed adjudication without changing the protocol.",
        "",
        "No production/live-trading claim is made.",
        "",
    ]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the frozen state-conditioned frequency adaptation v1 replay."
    )
    parser.add_argument("--state-pool", required=True, type=Path)
    parser.add_argument("--state-pool-sha256", required=True)
    parser.add_argument("--source-revision", required=True)
    parser.add_argument("--code-commit")
    parser.add_argument("--n-boot", type=int, default=2000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260908)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "experiments/state_frequency_adaptation_v1",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = datetime.now(timezone.utc)
    state_path = args.state_pool.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not state_path.is_file():
        raise StatePoolError(f"state pool not found: {state_path}")
    actual_state_sha = _sha256(state_path)
    if actual_state_sha.lower() != args.state_pool_sha256.lower():
        raise StatePoolError(
            f"state-pool SHA256 mismatch: expected {args.state_pool_sha256}, got {actual_state_sha}"
        )

    raw_state = _read_state_pool(state_path)
    state = validate_state_pool(raw_state)
    audit = _state_surface_audit(raw_state, state)

    if "source_revision" in raw_state.columns:
        revisions = sorted(
            set(raw_state["source_revision"].dropna().astype(str).str.strip()) - {""}
        )
        if revisions and revisions != [args.source_revision]:
            raise StatePoolError(
                f"state source_revision column disagrees with --source-revision: {revisions}"
            )

    primary_state = state.loc[
        state["symbol"].astype(str).isin(SYMBOLS) & state["state"].isin(ALLOWED_STATES)
    ].copy()
    if primary_state.empty:
        raise StatePoolError("no primary Unsafe/Recovering rows after validation")

    manifest_path = ROOT / "data/manifest.json"
    manifest_sha = _sha256(manifest_path)
    code_commit = _git_head(ROOT, args.code_commit)

    market_boundary: dict[str, dict[str, int]] = {}
    observation_parts: list[pd.DataFrame] = []
    market_ranges: dict[str, dict[str, object]] = {}

    for symbol in SYMBOLS:
        symbol_state = primary_state.loc[primary_state["symbol"].astype(str).eq(symbol)].copy()
        start = symbol_state["market_time_shanghai"].dt.strftime("%Y-%m-%d").min()
        end = symbol_state["market_time_shanghai"].dt.strftime("%Y-%m-%d").max()
        market = load_market_data(symbol, "1m", start, end)
        if market.empty:
            raise RuntimeError(f"verified 1m market data empty for {symbol} {start}..{end}")

        market_ranges[symbol] = {
            "start": start,
            "end": end,
            "market_rows": int(len(market)),
        }
        market_boundary[symbol] = _boundary_audit(market)

        for family in FAMILIES:
            for horizon in HORIZONS:
                obs = build_frequency_observations(
                    market,
                    symbol_state,
                    horizon=int(horizon),
                    family=family,
                )
                if not obs.empty:
                    observation_parts.append(obs)

    if not observation_parts:
        raise RuntimeError("fixed replay produced no observations")

    observations = pd.concat(observation_parts, ignore_index=True)
    raw_curve = summarize_observations(observations)
    raw_curve["turnover_units_per_decision"] = (
        raw_curve["turnover_units"] / raw_curve["n_decisions"]
    )
    raw_contrast = frequency_contrasts(raw_curve)

    matched_curve = seasonality_matched_summary(observations)
    matched_contrast = frequency_contrasts(matched_curve)

    raw_survival = cost_survival_summary(raw_curve)
    raw_survival.insert(0, "view", "raw")
    matched_survival = cost_survival_summary(matched_curve)
    matched_survival.insert(0, "view", "seasonality_matched")
    cost_survival = pd.concat([raw_survival, matched_survival], ignore_index=True)

    uncertainty = day_block_break_even_uncertainty(
        observations,
        n_boot=args.n_boot,
        seed=args.bootstrap_seed,
    )

    input_identity = {
        "state_pool": {
            "path": str(state_path),
            "sha256": actual_state_sha,
            "source_revision": args.source_revision,
        },
        "market_package": {
            "manifest_path": str(manifest_path),
            "manifest_sha256": manifest_sha,
            "ranges": market_ranges,
        },
        "code_commit": code_commit,
        "frozen_symbols": list(SYMBOLS),
        "frozen_horizons_minutes": list(HORIZONS),
        "frozen_families": list(FAMILIES),
    }
    audit["dense_same_segment_boundary_exclusion_timestamps_by_symbol_horizon"] = market_boundary
    audit["cross_segment_observations_in_output"] = int(
        (
            observations["session_segment"].isna()
            | ~observations["session_segment"].isin(["AM", "PM"])
        ).sum()
    )

    summary = {
        "status": "empirical_outputs_complete_adjudication_pending",
        "primary_adjudication": None,
        "protocol_complete": False,
        "raw_break_even_contrasts": _records(raw_contrast),
        "seasonality_matched_break_even_contrasts": _records(matched_contrast),
        "cost_survival": _records(cost_survival),
        "note": (
            "A protocol owner must select exactly one of the five frozen adjudications "
            "from the persisted evidence without changing the protocol."
        ),
    }

    frequency_path = output_dir / "frequency_curve.csv"
    matched_path = output_dir / "seasonality_matched_curve.csv"
    survival_path = output_dir / "cost_survival.csv"
    uncertainty_path = output_dir / "uncertainty.csv"
    input_path = output_dir / "input_identity.json"
    audit_path = output_dir / "state_pool_audit.json"
    summary_path = output_dir / "summary.json"
    card_path = output_dir / "RESULT_CARD.md"

    raw_curve.to_csv(frequency_path, index=False)
    matched_curve.to_csv(matched_path, index=False)
    cost_survival.to_csv(survival_path, index=False)
    uncertainty.to_csv(uncertainty_path, index=False)
    _write_json(input_path, input_identity)
    _write_json(audit_path, audit)
    _write_json(summary_path, summary)
    card_path.write_text(
        _result_card(
            observations,
            raw_curve,
            matched_curve,
            uncertainty,
            actual_state_sha,
            args.source_revision,
        ),
        encoding="utf-8",
    )

    finished = datetime.now(timezone.utc)
    output_paths = [
        card_path,
        summary_path,
        input_path,
        audit_path,
        frequency_path,
        matched_path,
        survival_path,
        uncertainty_path,
    ]
    receipt = {
        "code_commit": code_commit,
        "command": [sys.executable, *sys.argv],
        "python": sys.version,
        "platform": platform.platform(),
        "package_versions": _package_versions(),
        "input_hashes": {
            "state_pool_sha256": actual_state_sha,
            "market_manifest_sha256": manifest_sha,
        },
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "exit_code": 0,
        "output_hashes_sha256": {path.name: _sha256(path) for path in output_paths},
        "receipt_self_hash_excluded": True,
        "environment": {"cwd": os.getcwd()},
    }
    _write_json(output_dir / "execution_receipt.json", receipt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
