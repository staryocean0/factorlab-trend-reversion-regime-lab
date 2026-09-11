# R1_B MO — DataHub primary source route — 2026-09-11

Research identity: `rmr_R1B_MO_convex_impulse_mapping_v1`

Routing decision: `docs/governance/R1B_MO_SOURCE_ROUTING_DECISION_20260911.json`

## What DataHub provides (primary)

Pinned product for MO executable L1 research:

| Field | Value |
|---|---|
| product_id | `cffex_index_option_trade_activity_3s` |
| dataset_version | `derivative_trade_activity_cn_cffex_3s_20191223_20260825_v5_20260830` |
| MO effective window | **2022-07-22 .. 2026-08-25** |
| bid/ask | `bid_price_1`, `ask_price_1`, `bid_volume_1`, `ask_volume_1` |
| source filter | `source_kind=baidu_cffex_500ms_derived_trade_activity_3s` only |
| contract master | `derivative_contract_identity_cn_cffex_index_option_20191223_20260825_v2_20260826` |

Machine binding: `docs/governance/R1B_MO_DATAHUB_SOURCE_BINDING_v1.json`

Field mapping: `docs/governance/R1B_MO_DATAHUB_TRADE_ACTIVITY_MAPPING_v1.json`

Fee contract: `docs/governance/R1B_MO_FEE_CONTRACT@1.0.json` (RMB 14 / contract / open or close leg)

Adapter: `research/r1b_mo_data_admission/adapt_datahub_mo_trade_activity.py`

Export helper: `research/r1b_mo_data_admission/export_datahub_mo_month.py`

## Tail waiver

User waived the nominal study tail **2026-08-26 .. 2026-09-10** on 2026-09-11. Research intentionally ends at the pinned DataHub dataset tail **2026-08-25**.

## What this is not

- Not a CIIS/CFFEX Level-2 snapshot byte delivery (five-depth official layout).
- Not admission PASS by itself; a complete manifest + validator receipt is still required.
- Not production authority.

## CIIS relationship

CIIS/CFFEX official Level-2 order remains documented under `docs/research/R1B_MO_CIIS_ORDER_REQUEST_PACKAGE_20260911.md` as an **optional** official-provenance supplement. It is not required for current bid1/ask1 work when local DataHub is available.

## Relationship to 000852 index data

Index bars for `000852.SH` continue to serve R1_B event timing and direction only. MO trade-activity is the separate instrument quote surface for premium execution.

## Remaining blocker

Populate a complete DataHub-backed admission manifest over the effective window and obtain validator PASS. Fee and tail are no longer open.

`BLACKBOX_query_count=3`
