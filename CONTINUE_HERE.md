# Continue here — one-day 2025-12-01 source files delivered; waiting cloud review

## Current frontier

Local pack: `data/etf_microstructure_sample_20251201_v1/`. Cloud still has to hash the six parquet files and decide whether they close the observation gap. The last cloud verdict remains `UPSTREAM_EXPLANATION_PARTIALLY_VERIFIED_ONE_DAY_QUOTE_DELIVERY_PENDING` until that review runs.

User delivery `7bc9f893cf045e07479f251a8aa3a7c7e012d52a` contains actual source materials under `data/etf_upstream_evidence_v1/`. Cloud review has executed. Read:

1. `docs/research/ETF_UPSTREAM_CLOUD_REVIEW_20260912.md`
2. `docs/ops/evidence/etf_upstream_cloud_review_20260912/receipt.json`
3. `docs/ops/ETF_ONE_DAY_SOURCE_DELIVERY_20251201.md` — the request that this pack answers
4. `data/etf_microstructure_sample_20251201_v1/README.md`
5. `research/etf_upstream_review/README.md`

35 payload files/183,066 bytes plus manifest verified; 3 full text copies hashed; 4 excerpt blocks match full text; 20 fixed anomalies compared across supplied representations. Code/metadata-only source review and 14 boundary tests passed in run 34681596073. No new strategy prices or returns were read.

## What is now explained, and what is not

The 4ceca legacy bar-Z label denotes Shanghai wall clock under its delivered source contract. The 20 decoded labels match old examples. Do not apply that exception to all Z strings, knowledge timestamps or L2/tick products. The 1m contract rejects nonzero session offsets. The original raw ETF trade-to-bar bucket boundaries are not independently exchange-verified by a higher-frequency aggregation contract.

All 20 anomalies already occur in the imported Baidu 1m bars: OHLC/volume=0/amount=0 match canonical, only dataset_version differs. These are views of the same upstream, NOT independent vendors. Original zip/CSV members for those 20 timestamps remain unavailable; zero-volume cause remains UNKNOWN. A different date, 2025-12-01, now has L2/tick/index 3s extracts in `data/etf_microstructure_sample_20251201_v1/`; that is not the 20-sample vendor zip. The catalogue says lots on a limited inspected product set while old export says shares; historical units are not certified. Do not multiply guessed factors or reclassify zero records.

Producer assignments are now visible: ETF sample available_at equals the 2026 ingestion time; observed index minutes get same-day 15:30+08:00; filled rows get a synthetic bar label. These are not one homogeneous verified real-time publication field. Prior-close fill code passes bounded synthetic tests, not full production/PIT certification. End-label caps can place a 15:00:03 input in a 15:00 bar. No universal lookahead verdict has been made.

Full action/suspension history remains NOT_CERTIFIED. Supplied NAV/factor rows do not replace issuer notices. The fixed known-action repair and its zero-effect-on-published-cohorts finding remain unchanged.

## Exact next material, no repeat transfer

The six logical files are in `data/etf_microstructure_sample_20251201_v1/` (quotes 4823/4975, trades 10376/93639, index 3s 4748/4746). They are filtered source-day extracts, not 1m substitutes. Dictionaries, units, checkpoint/delta notes and same-day action UNKNOWN live in that pack. Cloud should hash the parquet files from a clean checkout; local row counts are not cloud verification.

Do not request the same five-year OHLCV pack or already delivered whitepaper again. One-day field/clock qualification does not require first certifying every five-year historical action, but it does not grant strategy or NAV-premium authority. No purchase, date expansion, 2026 candidate opening, fabricated quote or automatic outcome calculation.

## Preserved prior results and scope

R1_A remains `R1A_CURRENT_PRICE_FORMULATION_RESERVED_ACTIVE_DEVELOPMENT_PAUSED`. Closed R1_B/R2-directional/options and failed selected-cohort results remain closed. Known 2026 candidate stays metadata-only.

The 512100 2022-09-02 consolidation was separately repaired in `data/etf_source_actions_v2/`; proposed 2022-08-03 split was cancelled. Source-impact audit checked all 3098 pairs/21686 horizon rows; published memberships and 112 mean groups were unchanged. Do not redo it or describe that known action's effect as unquantified.

A one-day local quote/trade/index extract exists; it is not yet a cloud-qualified quote surface and grants no economic-deviation identification. No lead-lag, half-life, threshold, horizon, cost or profit test has been run. `BLACKBOX_query_count=3`, `production_authority=false`, `fresh_oos=false`.
