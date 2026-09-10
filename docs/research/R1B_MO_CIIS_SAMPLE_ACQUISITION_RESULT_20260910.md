# R1_B MO — CIIS CFFEX Snapshot public-sample acquisition result — 2026-09-10

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Scope: **non-event-conditioned source acquisition / schema discovery only**.

This result does not authorize an R1_B event join, option return/PnL, parameter search, BLACKBOX query #4, or production use.

`BLACKBOX_query_count=3`  
`production_authority=false`

## Result

The previously identified CIIS public CFFEX Level-2 Snapshot sample was re-checked from a GitHub-hosted runner.

The current CIIS sample-data page was successfully fetched only with TLS certificate verification bypassed because the CIIS HTTPS certificate chain did not validate on the hosted runner. The captured page still explicitly lists:

`20221206_Sample_CFF_Snapshot.xlsx`

The listed relative href resolves to:

`https://www.ciis.com.hk/hongkong/en/historicaldata1/sampledata/20221206_Sample_CFF_Snapshot.xlsx`

The current live download returns HTTP `404`.

Same-path origin variants were also probed:

- `https://www.ciis.com.hk/...` -> 404;
- `https://ciis.com.hk/...` -> 404;
- `http://www.ciis.com.hk/...` -> 404;
- `http://ciis.com.hk/...` -> 404.

An Internet Archive CDX lookup for the exact listed sample URL completed successfully but returned no captures (`[]`). No archived workbook bytes were therefore obtained.

## Frozen evidence

Evidence is stored under:

`research/r1b_mo_data_admission/source_samples/ciis_cffex_snapshot_20221206/`

Key receipts:

- `listing_receipt.json` — current page listing, resolved href, page SHA-256, TLS caveat;
- `live_download_status.txt` — current live 404 result;
- `live_variant_probe.tsv` — same-origin variant results;
- `internet_archive_cdx.json` — empty capture result;
- `sample_acquisition_receipt.json` — final acquisition state.

The final receipt state is:

`CURRENT_PUBLIC_LISTING_CONFIRMED_SAMPLE_BYTES_UNAVAILABLE_NOT_ADMITTED`

No XLSX bytes were acquired. Therefore there is still no workbook checksum, row count, sheet structure, or byte-level field mapping from this public sample.

## Interpretation

The source-discovery question is now narrower than before:

- CIIS still advertises the relevant CFFEX Level-2 Snapshot sample on its current official sample page;
- the advertised historical sample link is currently dead;
- automated same-origin recovery and exact-URL Internet Archive recovery did not produce the workbook;
- this is now an acquisition blocker, not an unresolved search question.

The next admissible source action is to obtain a **current equivalent non-event-conditioned CFFEX Snapshot sample or the full historical delivery directly from CIIS/CFFEX**, together with the current field dictionary / delivery semantics. The request must not include or condition on R1_B event timestamps.

The previously frozen full-data target remains all listed CSI1000 index option (`MO`) contracts from 2022-07-22 through 2026-09-10, with post-2026-09-11 prospective observations separately inventoried under the existing data-role freeze.

## Decision

`CIIS_PUBLIC_SAMPLE_LISTING_CONFIRMED_LINK_DEAD_EXTERNAL_DELIVERY_REQUIRED`

This is a source-acquisition result only. It does not change the mechanism certification, economic-test authority, BLACKBOX allocation, or production authority.
