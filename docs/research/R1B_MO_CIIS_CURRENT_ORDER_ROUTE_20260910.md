# R1_B MO — current CIIS official order route and delivery-epoch constraint — 2026-09-10

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Scope: source acquisition / admission only. No R1_B event join, option PnL, parameter search, BLACKBOX query #4, or production authority is created by this note.

## Current official route re-confirmed

The current CIIS Historical Data pages state that CFFEX historical data are official products directly provided by CFFEX and that **CFFEX Level-2 Intra-Day Snapshot Historical Data** are available from **2010-04-16** onward.

Current official CIIS historical-data page:

- https://www.ciis.com.hk/hongkong/en/historicaldata1/index.shtml

Current delivery routes listed by CIIS:

- cloud platform for the latest two weeks under ongoing subscription;
- external storage media;
- FTP/SFTP for smaller deliveries.

The current page lists:

- `Historical_Data_Product_Manual_v4_20260819.pdf`;
- `Historical Data Order Form (Form HD) (v20260820).xlsx`;
- contact: `hd@ciis.com.hk`.

The current public pricing page states that CFFEX Level-2 intraday snapshot history is charged in three-month units, with a different rate for the recent three calendar years versus earlier history. This note records only route feasibility; it does not authorize a purchase or select a commercial package.

## Important delivery-format finding

A 2026 CIIS Historical Data Product Manual available from the same official domain documents a format transition effective **2024-07-08** for CFFEX historical delivery naming/layout and points away from the legacy Snapshot layout toward the newer delivery convention.

Because the required MO history spans 2022-07-22 through 2026-09-10, the source-admission problem must therefore be treated as at least two physical delivery epochs rather than one assumed invariant CSV schema.

Frozen governance:

- `docs/governance/R1B_MO_CIIS_DELIVERY_EPOCH_FREEZE_20260910.json`

The two historical epochs are:

1. `LEGACY_CFFEX_SNAPSHOT`: 2022-07-22 through 2024-07-07;
2. `POST_TRANSITION_CFFEX_DELIVERY`: 2024-07-08 through 2026-09-10.

Each epoch must independently prove physical bid/ask column mapping, timestamp semantics, trading status, zero/missing quote semantics, and contract-master/expiry mapping before canonical concatenation.

A PASS for one epoch cannot waive unresolved fields in the other.

## Exact non-event-conditioned request

The next admissible external request should ask CIIS for either a current non-event-conditioned schema sample covering both delivery eras or the full official delivery for all listed MO contracts, together with the applicable field dictionary/layout documentation for each era.

Suggested request content:

> Please provide China Financial Futures Exchange (CFFEX) Level-2 Intra-Day Snapshot Historical Data for all listed CSI1000 index option (MO) contracts from 2022-07-22 through 2026-09-10. The research requires exchange timestamps, best bid/ask price and size, last price, volume, open interest, quote/trading-status semantics, and contract expiry/master information. Because the requested period crosses the historical delivery-format transition around 2024-07-08, please also provide the file-layout / field dictionary applicable to each delivery era, including physical expansion of bid/ask depth arrays and zero/missing quote semantics. A non-event-conditioned sample for each era is acceptable for schema verification before a full order.

Do not provide R1_B event timestamps to the vendor and do not condition the requested sample on research events.

## Current blocker classification

The old public sample URL has already been exhausted (live 404 plus same-origin variants plus exact-URL Internet Archive lookup). Current official CIIS pages nevertheless confirm that the CFFEX Level-2 historical product and current order route remain active.

Therefore the blocker is now classified as:

`PUBLIC_SAMPLE_RECOVERY_EXHAUSTED_CURRENT_OFFICIAL_ORDER_ROUTE_CONFIRMED_EXTERNAL_DELIVERY_REQUIRED`

This is no longer an open-ended web-discovery problem.

`BLACKBOX_query_count=3`.
`production_authority=false`.
