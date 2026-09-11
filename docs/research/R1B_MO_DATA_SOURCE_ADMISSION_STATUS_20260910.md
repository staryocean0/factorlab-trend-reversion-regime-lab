# R1_B MO data-source admission status — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Decision: **NO MO INTRADAY BID/ASK DATA ADMITTED**.

Empirical option outcome test authorized: **no**.

`BLACKBOX_query_count=3`  
`production_authority=false`

## What is established

- CFFEX Level-2 has the top-of-book/depth, size, last-price, volume and open-interest capability required by the frozen primary mapping.
- CIIS remains an active official distribution route for CFFEX Level-2 Intra-Day Snapshot Historical Data.
- Current CIIS pages list a current Historical Data Product Manual, Order Form and `hd@ciis.com.hk` contact route.
- The old public sample `20221206_Sample_CFF_Snapshot.xlsx` remains listed but its live URL returns 404; same-path origin variants and exact-URL Internet Archive recovery did not recover bytes.
- The public-sample recovery route is therefore exhausted. Its receipts/raw probes are preserved under `docs/archive/ciis_public_sample_recovery_20260910/`.
- A current CIIS product manual documents a CFFEX historical delivery-format transition effective 2024-07-08.

## Frozen physical delivery epochs

The requested MO history must not be treated as one invariant physical layout:

1. `LEGACY_CFFEX_SNAPSHOT`: 2022-07-22 .. 2024-07-07
2. `POST_TRANSITION_CFFEX_DELIVERY`: 2024-07-08 .. 2026-09-10

Each epoch requires its own delivered/source-dictionary mapping and independent schema/provenance check before canonical concatenation.

Freeze: `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`.

## Remaining admission blockers

Real non-event-conditioned sample/full-delivery evidence still must establish, per epoch:

- raw bytes, SHA-256, byte size, row count and package/version identity;
- physical bid1 / bid1_size / ask1 / ask1_size mapping;
- MO `SecurityID` / option identity;
- exchange-local timestamp format and precision;
- volume and open-interest semantics;
- zero/missing quote encoding;
- trading/quote-status semantics;
- authoritative contract-master / expiry mapping;
- correction/republication/version semantics;
- complete historical fee contract, including actual broker/customer commission.

No minute OHLC, last price or midpoint can substitute for executable bid/ask in the primary mapping.

## Active acquisition route

Read:

- `docs/research/R1B_MO_CFFEX_ACQUISITION_SPEC_20260910.md`
- `docs/research/R1B_MO_CIIS_CURRENT_ORDER_ROUTE_20260910.md`
- GitHub issue #7

Current source-level state:

`PUBLIC_SAMPLE_RECOVERY_EXHAUSTED_CURRENT_OFFICIAL_ORDER_ROUTE_CONFIRMED_EXTERNAL_DELIVERY_REQUIRED`

## Mechanical gate

Protocol: `docs/governance/R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`.

Adapters:

- `research/r1b_mo_data_admission/adapt_cffex_snapshot.py`
- `research/r1b_mo_data_admission/adapt_cffex_snapshot_epochs.py`

Validator:

- `research/r1b_mo_data_admission/validate_mo_quote_source.py`

CI run `34450248565` passed after the multi-epoch fail-closed adapter/test addition.

Canonicalization success remains **not admitted**. Only a complete validator PASS after provenance/schema/fee closure can unlock a separate pre-execution freeze; it does not itself authorize PnL.
