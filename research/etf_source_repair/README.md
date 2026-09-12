# ETF source correction and historical impact audit

Read `docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md` and `docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json`.

The actual known-action correction is in `data/etf_source_actions_v2/`. It fixes the missing 512100 2022-09-02 consolidation while explicitly excluding the cancelled 2022-08-03 proposal. It does not certify exhaustive actions or upstream quote/volume/time semantics.

Decisive raw-source impact run: `34677079296`; code `7b66fa290ddeea363323bcb89fdc15f12a896384`. All 3,098 frozen pairs and 21,686 pair-horizon records were checked under the ORIGINAL exclusion rules. No included endpoint/full-path cohort changed. All 112 recomputed published mean groups are unchanged; no new return population or model was opened.

## Read-only validation

```bash
PYTHONPATH=src:. python -m pytest -q tests/test_etf_source_repair.py tests/test_etf_source_repair_retained.py
PYTHONPATH=src:. python research/etf_source_repair/verify_retained.py
```

This verifies retained evidence, 125 pinned baseline files and independent action-boundary/group-count arithmetic. It is not another independent market experiment and does not repeat all original OHLC quantile calculations.

A deliberate full original audit reproduction is also available, in a NEW directory, with baseline Git tree present:

```bash
git fetch --no-tags --filter=blob:none --depth=1 origin ef18bf905e9e427153650d5538a996249bb6a901
PYTHONPATH=src:. python research/etf_source_repair/audit.py --output /tmp/etf-source-repair-new
```

The initial output is retained at `docs/ops/evidence/etf_source_repair_20260912/`; never overwrite it. The script pins old inputs, reads only 2021-2025 index partitions and the delivered ETF files, reuses saved pairs and returns, and does not generate new signals or fit models. The original 512100 full-path and all-horizon common-cohort outcome blocks stay closed.

The scanner's 44 code/workflow text hits are a bounded consumer inventory, not proof that every external or dynamically imported consumer has been identified. Reviewed direct consumers use ETF prices for endpoint/path measurement, not generating R1 signals; the forecasting/development lanes use index inputs. Source/exporter semantics and exhaustive action coverage still require source documentation.
