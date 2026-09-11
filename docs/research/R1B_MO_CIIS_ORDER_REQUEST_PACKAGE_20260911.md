# R1_B MO — CIIS/CFFEX order request package — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Purpose: **optional** external action package for the account holder if official CIIS/CFFEX byte-layout provenance is desired later. **Not required** while local pinned DataHub MO L1 is the primary route (`docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`). Sending this order creates **no** admission PASS, option PnL authority, BLACKBOX query #4, or production authority.

`production_authority=false`

## Blocker resolved locally

The old dead href `.../sampledata/20221206_Sample_CFF_Snapshot.xlsx` was superseded on the current CIIS Sample Data page by:

`https://www.ciis.com.hk/hongkong/en/uploadfiles/202212/12/2022121215374452718660.xlsx`

That legacy positional workbook was downloaded locally on 2026-09-11 (SHA-256 `b0aa832d5ca875cc017f97baf3fa83e2762548d6835c58591e4736fa0df1021b`, 628,017 bytes, 2,999 rows / 1,621 MO rows). It supports **legacy epoch schema mapping only**; it does not substitute for the full 2022-07-22..2026-09-10 delivery and contains no post-2024-07-08 layout.

## Optional external action (user-only, not a current blocker)

If official CIIS delivery is still wanted for provenance audit, email **hd@ciis.com.hk** with the completed order form and the request below.

Attachments to prepare locally (already downloaded for checksum inventory; do not expose private account fields in the public repo):

| Artifact | URL | Local SHA-256 |
| --- | --- | --- |
| Historical Data Product Manual v4 (2026-08-19) | https://www.ciis.com.hk/hongkong/en/uploadfiles/202605/20/2026052016504182474392.pdf | `7df1736c902004cee25b5010cde01fe64b37a7fa000d028742f19d71de6cc707` |
| Historical Data Order Form (Form HD) v20260820 | https://www.ciis.com.hk/hongkong/en/uploadfiles/202608/24/2026082405161079242257.xlsx | `43a749f3802d6669c7707ca7581fb38d245de92bec7233af296f0279f15da192` |

## Exact product request

> Product: **China Financial Futures Exchange (CFFEX) Level-2 Intra-Day Snapshot Historical Data**
>
> Underlying scope: **all listed CSI1000 index option (MO) contracts**
>
> Historical window: **2022-07-22 through 2026-09-10** (Asia/Shanghai observation dates)
>
> Required fields per delivery era: SecurityID / contract code, exchange-local DateTime with documented precision/timezone, physical best bid price/size and best ask price/size, LastPrice, Volume, OpenInterest, and any native quote/trading-status fields; if absent, provide the official dictionary statement.
>
> Because the window crosses the documented delivery-format transition around **2024-07-08**, please provide **separate field-layout documentation and, if possible, one non-event-conditioned sample file for each era**:
>
> 1. legacy era: 2022-07-22 .. 2024-07-07
> 2. post-transition era: 2024-07-08 .. 2026-09-10
>
> Also provide contract master / expiry mapping or an official rule reference sufficient to reconstruct expiry deterministically.
>
> Do **not** condition the sample on any research event list. This request is for instrument-data admission only.

## Delivery handling on receipt

1. Preserve raw bytes unchanged under `data/r1b_mo_acquisition/raw/` (local only; not committed to public Git).
2. Record SHA-256, byte size, row count, and package/version metadata per epoch.
3. Map each epoch independently (`docs/governance/R1B_MO_LEGACY_CFFEX_SNAPSHOT_MAPPING_v1.json` is legacy-sample-only).
4. Run `prepare_ciis_legacy_cff_snapshot.py` (legacy XLSX only), `adapt_cffex_snapshot.py`, `adapt_cffex_snapshot_epochs.py`, then `validate_mo_quote_source.py`.
5. Freeze fee contract before any event-conditioned inspection.

## Fee materials still required from user/broker

Exchange launch notice `http://www.cffex.com.cn/cn/ywtz/20220718/28904.html` confirms MO trading fee RMB 15/contract and exercise/assignment RMB 2/contract at launch, with declaration fee not charged. July 2024 official fee table matches the option fee basis. Broker/customer historical commission remains **unresolved** and must be supplied by the account holder; do not substitute another broker's public schedule.

`BLACKBOX_query_count=3`
