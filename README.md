# FactorLab Trend–Reversion Regime Lab

## Current frontier

**Known ETF action correction and historical impact audit completed; upstream source qualification remains incomplete.**

`KNOWN_ACTION_REPAIRED_PUBLISHED_MEMBERSHIP_UNCHANGED_SOURCE_SEMANTICS_PENDING`

The missing 512100 2022-09-02 consolidation/suspension is recorded in `data/etf_source_actions_v2/` and the source overlay. The cancelled 2022-08-03 split is NOT applied. No raw price, old action file, signal or old result was overwritten.

All 3,098 original pairs and 21,686 horizon records were checked. No existing included ETF endpoint/full-path sample changed; all 112 published mean groups are unchanged by this specific correction. Source completeness is still NOT certified; old `corporate_actions_complete=true` is historical input, not new-research admission.

Read `CONTINUE_HERE.md` and `docs/research/ETF_SOURCE_REPAIR_IMPACT_REVIEW_20260912.md`. Actual corrected known-action files and their hashes are in `data/etf_source_actions_v2/manifest.json`; the complete impact ledger is in `docs/ops/evidence/etf_source_repair_20260912/`.

The ETF/index relative-price direction remains measurement-only and blocked for economic dislocation/repair identification. Existing OHLCV does not provide synchronous bid/ask, trade or reference-valuation evidence. No routine re-transfer of historical CSVs is needed. Precise upstream documentation gaps are listed in `docs/ops/ETF_UPSTREAM_SEMANTICS_HANDOFF_20260912.md`.

R1_A remains an unconfirmed historical lead with active development paused. R1/R2 mechanism records and all closed R1_B/R2-directional/option studies remain preserved. No automatic replacement strategy, confirmation clock, horizon selection or 2026 outcome opening.

`BLACKBOX_query_count=3`; `production_authority=false`; `fresh_oos=false`.
