# R1_B MO data-source admission status — 2026-09-11 (updated)

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Decision: **NO MO INTRADAY BID/ASK DATA ADMITTED** (manifest/validator PASS still required)

Empirical option outcome test authorized: **no**

`BLACKBOX_query_count=3`  
`production_authority=false`

## Source routing (user decision)

Primary route: **local pinned DataHub MO L1 trade-activity**  
Decision record: `docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`

CIIS/CFFEX Level-2 Snapshot order: **optional supplement only** — not a current blocker for bid1/ask1 admission.

## Effective study window

| Boundary | Date |
|---|---|
| MO quote start | 2022-07-22 |
| MO quote end (effective) | **2026-08-25** |
| Nominal tail superseded | 2026-09-10 (user waived) |

## Fee contract

**Frozen** at RMB **14 / contract / open leg** and RMB **14 / contract / close leg**.  
Machine contract: `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json`  
Human summary: `docs/research/R1B_MO_FEE_SOURCE_STATUS_20260911.md`

## DataHub primary route

Pinned product `cffex_index_option_trade_activity_3s` (dataset_version `derivative_trade_activity_cn_cffex_3s_20191223_20260825_v5_20260830`).

| Artifact | Role |
| --- | --- |
| `docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json` | machine binding to pinned lake paths |
| `docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json` | field mapping |
| `research/r1b_mo_data_admission/adapt_datahub_mo_trade_activity.py` | canonical adapter |

Bounded evidence export for **2022-12**: 329,376 source rows → **328,706** canonical rows (`ADAPTED_NOT_ADMITTED`). Receipt: `docs/ops/evidence/r1b_mo_acquisition_20260911/datahub_adapter_receipt.json`.

## Legacy CIIS sample (auxiliary only)

Public legacy workbook supports epoch schema mapping only (`ADAPTED_NOT_ADMITTED`, 1,621 MO rows on 2022-12-06). It does not override DataHub as the primary consumption path.

## Validator

Template manifest still **FAIL**s until a complete DataHub-backed manifest and quote inventory are populated. Fee pending is no longer the blocker.

## Current source state

`DATAHUB_PRIMARY_SCHEMA_MAPPED_FEE_FROZEN_TAIL_WAIVED_ADMISSION_MANIFEST_REQUIRED`

## Next local step

Materialize/bind full DataHub MO window through 2026-08-25, populate manifest with frozen fee contract, run `validate_mo_quote_source.py`.

`BLACKBOX_query_count=3`
