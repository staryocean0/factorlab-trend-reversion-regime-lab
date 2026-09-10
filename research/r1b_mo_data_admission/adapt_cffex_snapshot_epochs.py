#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from research.r1b_mo_data_admission.adapt_cffex_snapshot import adapt_snapshot


class EpochManifestError(ValueError):
    pass


@dataclass
class EpochReceipt:
    epoch_id: str
    status: str
    rows: int
    min_timestamp: str
    max_timestamp: str
    errors: list[str]


@dataclass
class MultiEpochReceipt:
    adapter_id: str
    status: str
    epoch_receipts: list[dict[str, Any]]
    output_rows: int
    errors: list[str]
    admission_receipt_created: bool = False
    empirical_option_outcome_test_authorized: bool = False
    blackbox_query_count: int = 3
    production_authority: bool = False


def _load_manifest(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise EpochManifestError("epoch manifest must be a JSON object")
    epochs = obj.get("epochs")
    if not isinstance(epochs, list) or len(epochs) < 2:
        raise EpochManifestError("epoch manifest must contain at least two epochs")
    return obj


def _validate_epoch_spec(spec: dict[str, Any]) -> None:
    required = ["epoch_id", "snapshot", "contract_master", "mapping", "start", "end"]
    missing = [key for key in required if not isinstance(spec.get(key), str) or not spec[key].strip()]
    if missing:
        raise EpochManifestError(f"epoch spec missing required string fields: {missing}")


def _validate_timestamp_bounds(frame: pd.DataFrame, start: str, end: str) -> tuple[str, str]:
    ts = pd.to_datetime(frame["timestamp"], errors="coerce")
    if ts.isna().any():
        raise EpochManifestError(f"canonical timestamp parse failed rows={int(ts.isna().sum())}")
    lo = pd.Timestamp(start)
    hi = pd.Timestamp(end) + pd.Timedelta(days=1) - pd.Timedelta(microseconds=1)
    outside = (ts < lo) | (ts > hi)
    if outside.any():
        sample = frame.loc[outside, "timestamp"].astype(str).head(5).tolist()
        raise EpochManifestError(
            f"epoch contains canonical timestamps outside frozen bounds {start}..{end}; sample={sample}"
        )
    return ts.min().isoformat(), ts.max().isoformat()


def adapt_epochs(manifest_path: Path) -> tuple[pd.DataFrame, MultiEpochReceipt]:
    errors: list[str] = []
    epoch_receipts: list[dict[str, Any]] = []
    frames: list[pd.DataFrame] = []

    try:
        manifest = _load_manifest(manifest_path)
        seen_ids: set[str] = set()
        ranges: list[tuple[pd.Timestamp, pd.Timestamp, str]] = []

        for spec in manifest["epochs"]:
            if not isinstance(spec, dict):
                raise EpochManifestError("each epoch spec must be a JSON object")
            _validate_epoch_spec(spec)
            epoch_id = spec["epoch_id"]
            if epoch_id in seen_ids:
                raise EpochManifestError(f"duplicate epoch_id: {epoch_id}")
            seen_ids.add(epoch_id)

            start = pd.Timestamp(spec["start"])
            end = pd.Timestamp(spec["end"])
            if end < start:
                raise EpochManifestError(f"epoch {epoch_id} has end before start")
            ranges.append((start, end, epoch_id))

        ranges.sort(key=lambda x: x[0])
        for previous, current in zip(ranges, ranges[1:]):
            if current[0] <= previous[1]:
                raise EpochManifestError(
                    f"epoch date ranges overlap: {previous[2]} and {current[2]}"
                )

        for spec in manifest["epochs"]:
            epoch_id = spec["epoch_id"]
            frame, receipt = adapt_snapshot(
                Path(spec["snapshot"]),
                Path(spec["contract_master"]),
                Path(spec["mapping"]),
            )
            if receipt.status != "ADAPTED_NOT_ADMITTED":
                epoch_receipts.append(
                    asdict(
                        EpochReceipt(
                            epoch_id=epoch_id,
                            status="FAIL_CLOSED",
                            rows=0,
                            min_timestamp="",
                            max_timestamp="",
                            errors=receipt.errors,
                        )
                    )
                )
                raise EpochManifestError(f"epoch {epoch_id} source adapter failed closed")

            min_ts, max_ts = _validate_timestamp_bounds(frame, spec["start"], spec["end"])
            tagged = frame.copy()
            tagged.insert(0, "source_epoch", epoch_id)
            frames.append(tagged)
            epoch_receipts.append(
                asdict(
                    EpochReceipt(
                        epoch_id=epoch_id,
                        status="ADAPTED_NOT_ADMITTED",
                        rows=len(tagged),
                        min_timestamp=min_ts,
                        max_timestamp=max_ts,
                        errors=[],
                    )
                )
            )

        output = pd.concat(frames, ignore_index=True)
        output = output.sort_values(["timestamp", "contract_code", "source_epoch"]).reset_index(drop=True)
        receipt = MultiEpochReceipt(
            adapter_id="rmr_R1B_MO_cffex_multi_epoch_adapter_v1",
            status="MULTI_EPOCH_ADAPTED_NOT_ADMITTED",
            epoch_receipts=epoch_receipts,
            output_rows=len(output),
            errors=errors,
        )
        return output, receipt
    except Exception as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
        receipt = MultiEpochReceipt(
            adapter_id="rmr_R1B_MO_cffex_multi_epoch_adapter_v1",
            status="FAIL_CLOSED",
            epoch_receipts=epoch_receipts,
            output_rows=0,
            errors=errors,
        )
        return pd.DataFrame(), receipt


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Canonicalize independently documented CFFEX/CIIS physical delivery epochs without "
            "assuming cross-era column identity. This tool never creates an admission PASS or "
            "authorizes option outcomes."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()

    output, receipt = adapt_epochs(args.manifest)
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_text(json.dumps(asdict(receipt), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if receipt.status == "FAIL_CLOSED":
        print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    print(json.dumps(asdict(receipt), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
