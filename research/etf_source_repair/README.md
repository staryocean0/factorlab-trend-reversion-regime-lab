# ETF source correction and historical impact audit

Read `docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md` and `docs/governance/ETF_ACTION_SOURCE_OVERLAY_V2_20260912.json`.

Actual known-action files are in `data/etf_source_actions_v2/`. They fix the missing 512100 2022-09-02 consolidation and exclude the cancelled 2022-08-03 proposal. Exhaustive actions and upstream quote/volume/time semantics remain uncertified.

Decisive raw-source impact run: `34677079296`; code `7b66fa290ddeea363323bcb89fdc15f12a896384`. All 3,098 frozen pairs and 21,686 pair-horizon records were checked under ORIGINAL exclusion rules. No included endpoint/full-path cohort changed. All 112 recomputed published mean groups are unchanged. No new return population or model was opened.

## Current read-only validation

```bash
git fetch --no-tags --filter=blob:none --depth=1 origin ef18bf905e9e427153650d5538a996249bb6a901
PYTHONPATH=src:. python -m pytest -q tests/test_etf_source_repair.py tests/test_etf_source_repair_retained.py
PYTHONPATH=src:. python research/etf_source_repair/verify_retained.py
```

This verifies retained evidence and 125 pinned baseline inputs, including one historical operational workflow checked from its baseline Git object; all other mounted scientific/source inputs remain byte-exact. It independently checks action-boundary and sample-count arithmetic. It is not another market experiment. See `REPLAY_METADATA_NOTE.md` for the retained failure and commit-specific inventory checks.

## Full decisive audit reproduction

Use a SEPARATE detached checkout of `7b66fa290ddeea363323bcb89fdc15f12a896384` with the original permitted source files, original workflow bytes and baseline Git tree available. Do not replace a user's working tree. Inside that historical checkout:

```bash
git fetch --no-tags --filter=blob:none --depth=1 origin ef18bf905e9e427153650d5538a996249bb6a901
PYTHONPATH=src:. python research/etf_source_repair/audit.py --output /tmp/etf-source-repair-new
```

The initial output is retained at `docs/ops/evidence/etf_source_repair_20260912/`; never overwrite it. The decisive script pins old inputs, reads only 2021-2025 index partitions and delivered ETF data, reuses saved pairs/returns, and generates no signal or fit. The blocked primary full-path and common-cohort outcomes stay closed.

The scanner's 44 code/workflow text hits are a bounded inventory, not proof that every external/dynamic consumer is identified. Reviewed direct consumers measure ETF endpoints/paths; frozen R1 signals and forecasting features use index inputs. Future source use requires the overlay, upstream documentation and qualified data roles.
