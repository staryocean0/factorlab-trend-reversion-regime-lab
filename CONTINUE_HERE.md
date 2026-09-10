# Continue here — reversal / mean-reversion bucket

## Current authority

This repository's current job is **real reversal / mean-reversion strategy research**.

Canonical certified mechanism identities:

- **R1** — `rmr_cross_scale_pullback_parent_integrity_v2`: intact trend parent + lower-scale counter-move recovery; BLACKBOX-certified mechanism.
- **R2** — `rmr_range_boundary_parent_integrity_v2`: intact range parent + boundary overshoot / failed acceptance / re-entry; BLACKBOX-certified mechanism.

Reusable BLACKBOX query count remains exactly **3**:

1. R1 PASS;
2. R5-C FAIL;
3. R2 PASS.

No query #4 is authorized.

`production_authority=false`.

## What is already closed — do not restart it

The repository has already tested and closed the following identities/families under their existing definitions:

- R1 immediate index-level economic translation family;
- R2 `rmr_R2_range_reentry_economic_translation_v1`;
- `rmr_unified_parent_normal_state_router_v1`;
- `rmr_R1B_temporal_impulse_completion_v1` on DEV;
- probability-threshold / probability-sizing rescue of certified restoration probabilities;
- simple horizon / delay / stop / target / cost / scale rescue of the closed execution families;
- broad automatic R8/R9 indicator generation;
- R3/R4 and other broad Stage-1 lanes already closed by their frozen reviews.

The important scientific distinction remains:

> certified restoration probability is not the same thing as a certified trading payoff.

## R5-B1 side-line closure — 2026-09-10

The migrated historical R5-B1 lead received its one authorized limited TRAIN/VALIDATION diagnostic using the exact frozen historical input.

Result:

`R5_B1_limited_diagnostic_not_supported_close_B1`

- daily breadth gate: PASS;
- anti-persistence monotonic-shape gate: FAIL (`Spearman = -0.7`, required `<= -0.80`);
- BLACKBOX not read;
- post-2020 rows not read for that diagnostic;
- no PnL/trading mapping.

Read:

- `docs/research/R5_B1_LIMITED_DIAGNOSTIC_RESULT_20260910.md`
- `research/rmr_r5_b1/outputs/limited_diagnostic_receipt.json`

Do not rescue R5-B1 by changing bins, lag windows, dates or thresholds.

## Current frontier — R1_B payoff-object / instrument theory

The authority chain after the certified mechanisms is:

1. R1/R2 index-level economic translations failed detailed validation;
2. unified common router failed detailed validation and was closed;
3. mechanism-to-execution diagnostic found R2 directional markouts worsen with horizon and found only R1_B to have a meaningful delayed positive right-tail component;
4. one causal R1_B S2-impulse-completion exit was tested on DEV and closed because the preregistered median-net gate failed, despite positive mean net and 5/6 positive annual means;
5. payoff-object theory review therefore requires a materially independent payoff/instrument theory before any new empirical economic test.

The current accepted theory identity is:

`rmr_R1B_MO_convex_impulse_mapping_v1`

Decision:

`R1B_MO_CONVEX_PAYOFF_THEORY_ACCEPTED_DATA_ADMISSION_REQUIRED`

Read:

- `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
- historical diagnostic/adjudication package under `docs/archive/rmr_migrated_from_star50_20260909/raw/docs/research/`

### Why MO, not IM

A CSI1000 `IM` futures mapping remains linear and would mostly change basis/cost/margin; under the present evidence that is too close to a cost rescue of the closed linear payoff family.

A long directional CSI1000 `MO` option is a materially different convex payoff object and can, in principle, map a right-tail restoration impulse while bounding downside. This is theory only; option premium/theta/volatility/spread can invalidate it.

## Data-admission infrastructure and source discovery — 2026-09-10

The repository has completed the **admission infrastructure and official-source capability review**, not the empirical option test.

Current facts:

- current repository inventory contains no MO historical intraday best-bid/best-ask tape;
- account-wide GitHub code search was re-run with multiple field/name variants and found no reusable MO quote tape in another current bucket;
- CFFEX's own Level-2 documentation confirms five-level bid prices, ask prices, bid sizes and ask sizes, plus last price, volume and open interest, with snapshot distribution twice per second / 500 ms;
- CFFEX official historical Level-2 Snapshot remains the target source family;
- China Investment Information Services Limited (CIIS) provides a concrete official-distribution route and states its CFFEX historical Level-2 Snapshot product is official data directly provided by CFFEX;
- CIIS publicly identifies `20221206_Sample_CFF_Snapshot.xlsx` and currently lists the CFFEX Level-2 Snapshot product as available from 2010-04-16;
- the 2022 CIIS product manual documents CFFEX `Snapshot.csv` fields including `SecurityID`, `DateTime`, `LastPrice`, `Volume`, `OpenInterest`, `BidPrice[5]`, `BidVolume[5]`, `AskPrice[5]`, and `AskVolume[5]`;
- the current CIIS sample page was re-checked on 2026-09-10 and still explicitly lists `20221206_Sample_CFF_Snapshot.xlsx`, but the listed live href and all same-path www/non-www HTTP/HTTPS variants return 404;
- an exact-URL Internet Archive CDX lookup returned no captures, so no sample XLSX bytes, checksum, row count or workbook-level mapping were recovered; the acquisition state is `CIIS_PUBLIC_SAMPLE_LISTING_CONFIRMED_LINK_DEAD_EXTERNAL_DELIVERY_REQUIRED`;
- current CIIS pages also confirm the official CFFEX Level-2 historical product remains active, list `Historical_Data_Product_Manual_v4_20260819.pdf`, `Historical Data Order Form (Form HD) (v20260820).xlsx`, and `hd@ciis.com.hk` as the current order/contact route;
- a 2026 CIIS product manual documents a CFFEX historical delivery-format transition effective 2024-07-08, so the requested 2022-07-22 through 2026-09-10 MO history must be admitted as at least two physical schema epochs rather than assumed to have one invariant CSV layout;
- one-minute/five-minute OHLC, last-price-only, midpoint-only, AKShare historical daily data, and Tushare minute OHLC cannot substitute for the primary executable quote tape.

Current source-level state:

`PUBLIC_SAMPLE_RECOVERY_EXHAUSTED_CURRENT_OFFICIAL_ORDER_ROUTE_CONFIRMED_EXTERNAL_DELIVERY_REQUIRED`

Frozen / implemented files:

- `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`
- `docs/governance/R1B_MO_ADMISSION_MANIFEST_TEMPLATE.json`
- `docs/governance/R1B_MO_DATA_ROLE_FREEZE_20260910.json`
- `docs/governance/R1B_MO_CFFEX_SOURCE_MAPPING_TEMPLATE.json`
- `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`
- `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260910.md`
- `docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`
- `docs/research/R1B_MO_CIIS_ACQUISITION_ROUTE_20260910.md`
- `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
- `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260910.md`
- `research/r1b_mo_data_admission/validate_mo_quote_source.py`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot.py`
- `tests/test_r1b_mo_data_admission.py`
- `tests/test_r1b_mo_cffex_adapter.py`

Admission infrastructure CI:

- original admission-gate CI run `34422130207`: PASS;
- source-adapter + admission-gate CI run `34424261376`: PASS.

The adapter is deliberately fail-closed. It requires actual delivered/source-dictionary mappings for unresolved fields and returns `ADAPTED_NOT_ADMITTED`, never an admission PASS. The current mapping template intentionally leaves physical bid/ask-array expansion, trading-status mapping, zero-quote semantics and contract-master expiry mapping unresolved until a real non-event-conditioned sample or delivery dictionary is inspected.

The 2024-07-08 delivery-format transition is now frozen explicitly: legacy and post-transition physical files require separate source-specific mappings and independent schema/provenance checks before canonical concatenation. A schema PASS for one epoch cannot waive unresolved fields in the other.

The data-role boundary was frozen **before any event-conditioned MO option outcome was inspected**:

- 2022-07-22 through 2026-09-10: reusable instrument-development evidence only;
- from 2026-09-11 onward: prospective instrument-validation evidence, provided the observation was genuinely generated after the freeze and paired post-freeze underlying data are separately admitted.

This freeze creates no new BLACKBOX allocation.

## Fee-contract status

The fee layer remains deliberately fail-closed.

Established evidence:

- CFFEX's July-2024 official fee table supports the shared CSI index-option exchange baseline of RMB 15/contract trading fee and RMB 2/contract exercise/assignment fee;
- CFFEX's rule index identifies the 2022 MO launch notice, while multiple CFFEX-member reproductions identify it as `中金所发〔2022〕41号` and report the same 15/2 exchange baseline at launch, with declaration/order fee temporarily not charged.

Not yet closed:

- the original official CFFEX launch-notice body or another complete official-CFFEX effective-period chain proving the applicable exchange fee schedule across the entire historical study window;
- the actual broker/customer historical commission schedule.

Therefore:

`R1B_MO_FEE_CONTRACT_PENDING_EXCHANGE_CHAIN_STRONG_PARTIAL_BROKER_UNRESOLVED`

Do not use 15 RMB as a complete historical all-in cost merely because it is the exchange baseline. Do not invent a broker markup.

## Exact next authorized action

**Do not run an option return study yet.**

The public-sample recovery route is exhausted. Current CIIS pages confirm that the official CFFEX Level-2 historical product and order channel remain active. Tracking issue: **#7**.

The next source action is:

1. obtain non-event-conditioned samples for both physical delivery epochs, or proceed to the official full delivery; do not repeat blind retrieval of the dead `20221206_Sample_CFF_Snapshot.xlsx` URL;
2. preserve raw bytes and record SHA-256, byte size, workbook/file structure and row count;
3. inspect only source schema/semantics — do **not** join sample rows to R1_B events;
4. resolve a separate physical mapping for `LEGACY_CFFEX_SNAPSHOT` (2022-07-22..2024-07-07) and `POST_TRANSITION_CFFEX_DELIVERY` (2024-07-08..2026-09-10), including level-1 bid/ask and sizes, MO `SecurityID`, contract master/expiry, zero/missing quotes and trading status;
5. fill source-specific mappings without changing the frozen canonical protocol;
6. run `adapt_cffex_snapshot.py`, or a period-aware successor only if the delivered post-transition format requires it; adapter success still means only `ADAPTED_NOT_ADMITTED`;
7. acquire/inventory the full CFFEX MO Level-2 historical package for all listed MO contracts through 2026-09-10, with post-2026-09-11 prospective observations separately inventoried;
8. populate the actual-source manifest and freeze the complete fee contract;
9. run `validate_mo_quote_source.py` and retain PASS/FAIL receipt.

Read the current route and epoch freeze before external acquisition:

- `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
- `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`
- GitHub issue `#7`.

In parallel, obtain the actual historical broker commission schedule and complete the official exchange fee effective-period chain.

Only a PASS admission receipt can unlock a **separate pre-execution freeze**. A PASS still does **not** itself authorize PnL, BLACKBOX #4, or production.

The primary R1_B option mapping may not substitute midpoint/last price for missing bid/ask after outcomes are seen and may not search strike, expiry/DTE, horizon, probability threshold, timing, stop, target, scale or time-of-day.

## Bucket boundary

Do not restart a generic K-line state recognizer here. Range/up/down causal state recognition belongs to `factorlab-two-wave-strategy-lab`.

Do not restart bottom-layer volatility/risk-state switching here. Unsafe/Recovering/HighVol risk research belongs to `factorlab-star50-filter-lab`.

The `kline-recognizer` v1-v13 research branches in this repository are mis-scoped historical evidence. They remain in Git history but no longer define current authority.

## Read first

1. `CONTINUE_HERE.md`
2. `docs/research/R1_R2_MIGRATION_NOTE_20260909.md`
3. `docs/research/R1B_MO_CONVEX_PAYOFF_THEORY_REVIEW_20260910.md`
4. `docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`
5. `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
6. `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`
7. `docs/research/R1B_MO_CIIS_SAMPLE_ACQUISITION_RESULT_20260910.md`
8. `docs/research/R1B_MO_DATA_SOURCE_ADMISSION_STATUS_20260910.md`
9. `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260910.md`
10. `docs/research/R5_B1_LIMITED_DIAGNOSTIC_RESULT_20260910.md`
11. `docs/DATA.md`
12. `docs/RESEARCH_GOVERNANCE.md`

`BLACKBOX_query_count=3`.
`production_authority=false`.
