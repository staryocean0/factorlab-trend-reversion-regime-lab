# R5-B1 frozen-input migration decision

Date: 2026-09-10

Status: **FROZEN BEFORE ANY R5-B1 LIMITED-DIAGNOSTIC OUTCOME WAS PRODUCED**

## Why this note exists

The R5-B1 limited diagnostic was originally prepared to prove row-for-row semantic equivalence between this repository's annual `data/market/5m/000852.SH/{2015..2020}.parquet` files and the historical R5 single-file input `data/development/5m_offset_0.parquet`.

Three execution attempts stopped before producing any B1 diagnostic outcome:

1. current schema name mismatch (`timestamp` vs `bar_end_shanghai`);
2. direct timestamp parsing failed the row-for-row identity gate;
3. the historically documented Shanghai-wall-clock adapter still failed the row-for-row identity gate.

The current annual files have the same Git blobs as the trend/reversion source files referenced by the historical bridge work. Therefore this is not treated as evidence that current market files were recently altered. It is treated as an unresolved identity mismatch between two historical data representations.

## Decision

Do **not** keep transforming or repairing the current annual market data to force equivalence. That would create an avoidable data-rescue path after observing identity failures.

Instead, migrate the exact historical R5 input into the repository that now owns R5 research and execute the already-preregistered limited diagnostic directly on that exact frozen input.

Frozen input identity:

- source historical repository: `staryocean0/factorlab-two-wave-strategy-lab`
- source frozen commit: `cf8397c12a9defa243dc272224dedebe6ccd3251`
- source path: `data/development/5m_offset_0.parquet`
- SHA256: `bea21fa9dd9532e21605511e07561b33d5569f86f69f5a487507531593b14c48`
- rows: `70114`
- symbol: `000852.SH`
- admitted dates: `2015-01-05..2020-12-31`

The exact frozen R5 runner is also migrated as immutable provenance:

- source path: `scripts/run_broad_rmr_R5_multiscale_serial_dependence.py`
- Git blob: `cd0ac94f7f8dc4fba7c9ee25701bcca02f551f2a`

Target ownership paths:

- `data/research_inputs/r5_b1/5m_offset_0.parquet`
- `research/rmr_r5_b1/frozen_source/run_broad_rmr_R5_multiscale_serial_dependence.py`
- `data/research_inputs/r5_b1/manifest.json`

## Scope of supersession

This decision supersedes only the **transport/equivalence prerequisite** in `R5_B1_LIMITED_DIAGNOSTIC_PROTOCOL_20260910.md`. It does not change any statistical definition or adjudication threshold in that protocol.

The limited diagnostic remains exactly:

1. validation-day breadth of B1 squared-error gain over B0;
2. TRAIN-quintile anti-persistence bins versus VALIDATION empirical next-return slope.

No model/window/lag/bin-count/date/threshold search is authorized.

`BLACKBOX_read=false`; `post_2020_read=false`; `PnL_read=false`; `production_authority=false`.
