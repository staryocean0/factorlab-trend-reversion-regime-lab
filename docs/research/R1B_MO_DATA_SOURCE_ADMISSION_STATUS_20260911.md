# R1_B MO data-source admission status — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Decision: **NO MO INTRADAY BID/ASK DATA ADMITTED**

Empirical option outcome test authorized: **no**

`BLACKBOX_query_count=3`  
`production_authority=false`

## Progress since 2026-09-10

### Legacy epoch — schema mapped on public sample only

The CIIS Sample Data page now resolves the legacy CFF Snapshot workbook through a live `uploadfiles/` URL (the older `sampledata/` href remains 404). Local bytes were acquired on 2026-09-11:

| Artifact | SHA-256 | Size | Rows |
| --- | --- | ---: | ---: |
| `20221206_Sample_CFF_Snapshot.xlsx` | `b0aa832d5ca875cc017f97baf3fa83e2762548d6835c58591e4736fa0df1021b` | 628,017 | 2,999 total / 1,621 MO |

Positional columns match CIIS manual **6.6.1** (41 fields). Physical mapping:

- `SecurityID` → contract code (`MO2302-C-6500` grammar verified);
- `DateTime` → `%Y%m%d%H%M%S%f` exchange-local timestamps (example `20221206093249400`);
- `BidPrice1` / `BidVolume1` / `AskPrice1` / `AskVolume1` → top-of-book;
- `LastPrice`, `Volume`, `OpenInterest` → diagnostic/cumulative fields per manual;
- native trading status **absent**; `DerivedQuoteStatus` documented in `docs/governance/R1B_MO_LEGACY_CFFEX_SNAPSHOT_MAPPING_v1.json`.

`prepare_ciis_legacy_cff_snapshot.py` + `adapt_cffex_snapshot.py` on the MO-only subset returned **`ADAPTED_NOT_ADMITTED`** (1,621 canonical rows). Receipt: `docs/ops/evidence/r1b_mo_acquisition_20260911/legacy_adapter_receipt.json`.

This is **not** full legacy-era delivery and **not** admission.

### Post-transition epoch — still blocked

No MO-bearing sample or delivery covering **2024-07-08 .. 2026-09-10** was obtained. The mislabeled `20171229_Sample_CFF_Snapshot.xlsx` upload is a 2017 tick layout without MO contracts and cannot proxy the post-transition snapshot era.

### DataHub rank-2 route — schema mapped, not admitted

Pinned DataHub product `cffex_index_option_trade_activity_3s` (dataset_version `derivative_trade_activity_cn_cffex_3s_20191223_20260825_v5_20260830`) provides MO L1 bid/ask in 3s trade-activity buckets. This is **not** a CIIS Level-2 snapshot byte delivery; it is the licensed rank-2 vendor feed under `R1B_MO_DATA_ADMISSION_PROTOCOL_V1.json`.

| Artifact | Role |
| --- | --- |
| `docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json` | machine binding to pinned lake paths |
| `docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json` | field mapping |
| `research/r1b_mo_data_admission/adapt_datahub_mo_trade_activity.py` | canonical adapter |
| `docs/research/R1B_MO_DATAHUB_ROUTE_20260911.md` | human route summary |

Bounded evidence export for **2022-12**: 329,376 source rows → **328,706** canonical rows after serving filter (`ADAPTED_NOT_ADMITTED`). Receipt: `docs/ops/evidence/r1b_mo_acquisition_20260911/datahub_adapter_receipt.json`. MO coverage on this pin ends **2026-08-25** (16-day tail gap to frozen window end).

CIIS dual-epoch order path remains open and is **not** replaced by DataHub wiring.

### Validator

`validate_mo_quote_source.py` on the unfilled manifest template correctly **FAIL**s (`docs/ops/evidence/r1b_mo_acquisition_20260911/validator_template_fail_receipt.json`). A PASS requires populated manifest, both epochs, frozen fee contract, and authoritative contract master.

## Current source state

`LEGACY_AND_DATAHUB_SCHEMA_MAPPED_NOT_ADMITTED_POST_EPOCH_FEE_AND_FULL_DELIVERY_REQUIRED`

## User-only blocker

Order full dual-epoch CIIS/CFFEX MO Level-2 Snapshot history using `docs/research/R1B_MO_CIIS_ORDER_REQUEST_PACKAGE_20260911.md`, and supply the account's historical broker commission schedule.

`BLACKBOX_query_count=3`
