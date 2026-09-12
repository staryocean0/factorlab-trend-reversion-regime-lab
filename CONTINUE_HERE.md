# Continue here — one-day raw delivery and cloud observation audit complete

## Current frontier

**Day files VERIFIED; restricted source-label replay available; terminal interval defect identified; real-time synchronization and NAV unqualified.**

Read `docs/research/ETF_ONE_DAY_CLOUD_REVIEW_20260912.md`, `docs/ops/evidence/etf_one_day_cloud_review_20260912/receipt.json`, and `research/etf_one_day_review/README.md`.

User delivery `6004b42b1a6d68e13ec602126292a3709d474b70` is at `data/etf_microstructure_sample_20251201_v1/`. All six Parquet files were read in fixed sparse checkout: 123,307 rows / 3,569,715 bytes, all hashes, identities and row counts verified. Full clone was not required; the user's aborted clone was not an acceptance result. Do not ask for re-transfer.

Decisive content audit run `34683088732`, code `54941508126b9499f1a8e6e65ea956d55bd394c2`; initial byte/row intake `34682669751`; 12 boundary tests. No returns, clock-shift fitting, date expansion or model fitting.

## Concrete findings

Two quotes: 4823/4975 rows, each 8 checkpoints. Two trades: 10376/93639 rows, positive prices/quantities, raw IDs unique; same-time multi-trades preserved. Index 3s: 4748/4746 actual rows. ETF native IDs use .SSE, index aliases .SH; original values unchanged.

Trade quantity sums exactly equal final quote cum_volume in source units: 296228774 / 2162018305. Internal consistency, NOT independent vendor or absolute shares/lots certification.

Restricted [09:30,11:30), [13:00,14:57) observed index target counts are 4738 each. Source-state interval/BBO coverage is 4736/4738 and 4738/4738. The primary's exact-label matches are zero because its quote grid has 2s remainder, not because it has no quote tape. No clock shift is fitted. No carry from breaks or future checkpoints. Coverage is relative to observed source labels, not proof of complete synchronized market observations.

Both final post-close valid intervals are reversed: 512100 15:00:02 -> 15:00:00; 588000 15:00:03 -> 15:00:00. Retain raw rows but never use them as valid intervals. This is the materializer's fixed-day-close boundary issue, not delivery corruption. Do not invent next-day or infinite endpoints.

Fixed 512100 13:26 anomaly: [13:25,13:26) has 0 tick rows, [13:26,13:27) has 22. Do not assign the latter automatically to a legacy end-labelled bar. Native 1m bucket and nonflat-zero-volume cause remain unresolved. No old prices/volumes were changed.

## Limits and next scope

Historical source-label state is not exchange receipt-time or independently known live availability. Time since last state change is not quote age. All iopv_raw are 0 and receipt_exact_pit false. Exact publication times, vendor archives, absolute units and complete day action/halt knowledge remain unqualified. Do not claim NAV discounts, lead-lag alpha or real-time profitability.

There is NO current local retransmission task. Existing one-day records permit further bounded field/quantity/minute-boundary reconciliation if separately authorized. Upstream terminal-state contract correction needs explicit versioning, not invented fills. No automatic broad acquisition, date changes, 2026 opening or new outcome experiments.

## Preserved history

The 35-file upstream evidence package and its fixed-source label explanation were accepted earlier; do not request them again. Source-specific bar-Z explanation is not a rule for all timestamps or products. ETF archive available_at represents ingestion; observed index minute available_at is producer day-end; fill rows use synthetic labels. No universal lookahead verdict has been made.

Known 512100 consolidation 2022-09-02 (new/old=0.36555) and resumption 2022-09-05 were already versioned. Proposed 2022-08-03 split was cancelled. Prior 3098-pair/21686-window impact audit found no published membership or mean change. Full five-year action completeness remains NOT_CERTIFIED.

R1_A remains `R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED`; original R1/R2 mechanisms, closed R1_B/R2-directional/options and failed selected-cohort results remain unchanged. Known 2026 candidate stays metadata-only. `BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`.

## Read-only reproduction

```bash
python -m unittest discover -s tests -p test_etf_one_day_review.py
python research/etf_one_day_review/audit.py --output /tmp/etf-one-day-new
```

Requires pyarrow. Fresh output directories only. Source files and historical evidence are never overwritten. Engineering success is not new market evidence.
