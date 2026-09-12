# Continue here — fixed-day field reconciliation completed

Latest task is complete: **day-end quantity equality does not establish intraday synchronization; legacy minutes are not fully reproduced; a restricted read-only source-label consumer is implemented.**

Read:
1. `docs/research/ETF_DAY_RECONCILIATION_REVIEW_20260912.md`
2. `docs/ops/evidence/etf_day_reconciliation_20260912/receipt.json`
3. `docs/governance/ETF_SOURCE_LABEL_CONSUMER_V1_20260912.json`
4. `research/etf_day_reconciliation/README.md`

## Actual completion

Freeze `17d87322e4ca8bac4e1299d2c76a4b05b886c9bc`; decisive run `34684308732`, code `fef8578c3caffd523f6db7f26c5a0f947de2be0a`. Eight CSVs plus receipt. Original six Parquet files and only 2025-12-01 legacy CSV observations enter calculations. All original raw bytes remain unchanged.

9,798 quote/tick accounting rows; 482 original fixed-day legacy rows times four predeclared minute conventions = 1,928 rows. Full phase and boundary accounting retained. No fitted multiplier, selected bucket or clock shift.

Continuous quote cumulative quantity exceeds the sum of recorded ticks at-or-before the quote label in 629/4,711 (512100) and 3,508/4,740 (588000) events; no negative differences. Final-day quantities remain equal. This is a representation mismatch inside each ETF's feeds, not an ETF/index lead-lag signal or proof of physical latency.

Under the declared price divisor, complete OHLC matches for [t-60s,t) are 158/235 and 77/237 printed minutes; all four scenario tables preserved, none certified as vendor truth. Raw-unit quantity inequality is not a data-error verdict because units remain unresolved. 512100 13:26 has no prints in the prior minute and different high/low/close in the next minute's22 prints; neither scenario reconstructs that legacy bar. Do not guess a repair.

## Restricted consumer, not upstream repair

`RestrictedSourceView` rejects reversed/empty/unknown intervals, future checkpoints, cross-phase carry, and fallback to an older state when the latest event is invalid. Consumer ends are clipped at declared phase boundaries; raw ends are not changed. 9,451 source events queryable within scope, 345 outside scope, two reversed terminal intervals retained but rejected. Two primary phase-end intervals clipped only in the consumer view. Observed-index-label coverage remains4736/4738 and4738/4738.

DataHub producer and source Parquet have NOT been patched. Source-label replay, offline valid_until and timestamp equality are NOT exact receipt-time/PIT, exchange synchronization, missing-message certification or executable prices.

## Current stop

This finite field/bucket accounting is finished; do not endlessly rerun it or try new shifts/bucket conventions until one matches. Existing sources are usable for explicitly limited historical observation, not automatically a unified realtime or vendor-certified minute feed. Exact publication times, original vendor members, units, complete action calendars and nonzero IOPV remain unqualified. No returns, date expansion, 2026 opening, acquisition or new empirical candidate follows automatically.

No new local transfer task. Five-year CSVs, source docs and the six day files are already delivered. A new study must separately state its estimand and source assumptions before authorization; missing source facts cannot be filled by optimizing an alignment.

## Preserved history

R1_A remains `R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED`; closed R1_B/R2/options and selected-cohort failures remain closed. Known512100 2022-09-02 consolidation/new-old0.36555 and prior published-result zero-impact audit are complete;2022-08-03 proposal was cancelled. Do not repeat that repair. Original sources/manifests/freezes/receipts remain intact; old complete=true does not admit new studies.

`BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`. Engineering replay is not independent strategy evidence.
